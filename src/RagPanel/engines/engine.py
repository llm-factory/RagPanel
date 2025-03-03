from abc import abstractmethod
from pydantic import BaseModel
from .chat_engine import ChatEngine
from ..utils.protocol import StrModel
from cardinal import AutoStorage, AutoVectorStore, DenseRetriever, BaseCollector, EmbedOpenAI
from ..utils.exception import (
    DatabaseConnectionError, 
    DatabaseNotFoundError,
    DatabaseNotInitializedError,
    StorageConnectionError,
    VectorStoreConnectionError
)


class BaseEngine:
    def __init__(self, collection="init"):
        self._splitter = None
        self.collection = collection
        self._storage = None
        self._vectorstore = None
        self._retriever = None
        self._graph_processor = None
        self.chat_engine = ChatEngine(self, "history_init")
        self.supported_storages = [
            "redis",
            "es"
        ]
        self.supported_vectorstores = [
            "chroma",
            "milvus"
        ]
        self.supported_graph_storages = [
            "None",
            "neo4j"
        ]

    def create_database(self):
        try:
            self._storage = AutoStorage[BaseModel](self.collection)
        except Exception as e:
            raise StorageConnectionError(f"Storage connection failed: {str(e)}")
            
        try:
            self._vectorstore = AutoVectorStore[BaseModel](self.collection)
        except Exception as e:
            raise VectorStoreConnectionError(f"Vector store connection failed: {str(e)}")
            
        self._retriever = DenseRetriever[BaseModel](vectorstore_name=self.collection, threshold=1.0)
        self.chat_engine.name = "history_" + self.collection
        self.chat_engine.collector = BaseCollector(storage_name="history_" + self.collection)
        
    def check_database(self):
        if self._storage is None or self._vectorstore is None or self._retriever is None:
            self.create_database()

    def clear_database(self):
        self.check_database()
        self.destroy_database()
        self.create_database()

    def destroy_database(self):
        self.check_database()
        if not self._storage.exists():
            self._storage = None
            self._vectorstore = None
            raise DatabaseNotFoundError("Database does not exist")
        self._storage.destroy()
        self._vectorstore.destroy()
        if self._graph_processor is not None:
            self._graph_processor.destroy()
        
    @abstractmethod
    def insert(self):
        """
            read, split and embed files
        """
        ...
        
    def graph_insert(self, file_contents):
        from ..utils import GraphProcessor
        collection = self.collection
        self.collection = "graph_" + collection
        self.create_database()
        self._graph_processor = GraphProcessor("en", 1, self.collection)
        self.collection = collection
        entities, relations = self._graph_processor.extract_graph(file_contents)
        new_entities = self._graph_processor.insert_entities(entities)
        self._vectorstore.insert(new_entities, [StrModel(string=e_name) for e_name in new_entities])
        self._graph_processor.insert_relations(relations)
        reports = self._graph_processor.generater_community_report()
        self._storage.insert(reports.keys(), [StrModel(string=report) for report in reports.values()])
        
    def graph_search(self, query, top_k, mode, threshold = None):
        self.check_database()
        tmp_threshold = self._retriever._threshold
        if threshold is not None:
            self._retriever._threshold = threshold
        from ..utils import GraphProcessor
        self._graph_processor = GraphProcessor("en", 1, self.collection)
        if mode == 'local':
            candidate_entities_name = self._retriever.retrieve(query=query, top_k=top_k)
            top_community_ids = self._graph_processor.local_search(candidate_entities_name, top_k)
            docs = []
            for community_id in top_community_ids:
                report = self._storage.query(f"Cluster {community_id}").string
                docs.append({"id": community_id, "content": report})
            self._retriever._threshold = tmp_threshold
            return docs
        else:
            self._retriever._threshold = tmp_threshold
            raise NotImplementedError

    def search(self, query, top_k, reranker, threshold = None):
        self.check_database()
        tmp_threshold = self._retriever._threshold
        if threshold is not None:
            self._retriever._threshold = threshold
        doc_indexes = self._retriever.retrieve(query=query, top_k=top_k)
        docs = []
        for index in doc_indexes:
            doc_id = index.doc_id
            doc = self._storage.query(key=doc_id).content
            docs.append({"id": doc_id, "content": doc})
        self._retriever._threshold = tmp_threshold
        if reranker == 'cohere':
            from ..utils.reranker import rerank
            docs = rerank(docs)
        return docs

    def launch_app(self, collection, host, port):
        from ..api.app import launch_app
        launch_app(self, collection, host=host, port=port)
