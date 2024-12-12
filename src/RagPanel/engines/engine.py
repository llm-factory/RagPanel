from abc import abstractmethod
from pydantic import BaseModel
from .chat_engine import ChatEngine
from ..utils.protocol import StrModel
from cardinal import AutoStorage, AutoVectorStore, DenseRetriever, BaseCollector, EmbedOpenAI


class BaseEngine:
    def __init__(self):
        self._splitter = None
        self.collection = None
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

    def create_database(self, collection):
        self._storage = AutoStorage[BaseModel](collection)
        self._vectorstore = AutoVectorStore[BaseModel](collection)
        self._retriever = DenseRetriever[BaseModel](vectorstore_name=collection, threshold=1.0)
        self.chat_engine.name = "history_" + collection
        self.chat_engine.collector = BaseCollector(storage_name="history_" + collection)
        self.collection = collection
        
    def check_database(self):
        if self._storage is None or self._vectorstore is None or self._retriever is None:
            raise ValueError("Please create a database first")
        self._vectorstore._vectorstore._vectorizer = EmbedOpenAI(batch_size=1000)
        self._retriever._vectorstore = self._vectorstore

    def clear_database(self):
        self.destroy_database()
        try:
            self._storage = AutoStorage[BaseModel](self.collection)
        except Exception:
            raise TimeoutError("storage connection error")
        try:
            self._vectorstore = AutoVectorStore[BaseModel](self.collection)
        except Exception:
            raise TimeoutError("vectorstore connection error")

    def destroy_database(self):
        self.check_database()
        if not self._storage.exists():
            self._storage = None
            self._vectorstore = None
            return
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
        self._graph_processor = GraphProcessor("en", 1, self.collection)
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
            top_community_reports = [self._storage.query(f"Cluster {community_id}").string for community_id in top_community_ids]
            self._retriever._threshold = tmp_threshold
            return "\n".join(top_community_reports)
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
