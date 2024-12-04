from abc import abstractmethod
from .chat_engine import ChatEngine
from ..utils.protocol import DocIndex, Document
from cardinal import AutoStorage, AutoVectorStore, DenseRetriever, BaseCollector


class BaseEngine:
    def __init__(self):
        self._splitter = None
        self.collection = None
        self._storage = None
        self._vectorstore = None
        self._retriever = None
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
        self._storage = AutoStorage[Document](collection)
        self._vectorstore = AutoVectorStore[DocIndex](collection)
        self._retriever = DenseRetriever[DocIndex](vectorstore_name=collection, threshold=1.0)
        self.chat_engine.name = "history_" + collection
        self.chat_engine.collector = BaseCollector(storage_name="history_" + collection)
        self.collection = collection
        
    def check_database(self):
        if self._storage is None or self._vectorstore is None or self._retriever is None:
            raise ValueError("Please create a database first")

    def clear_database(self):
        self.destroy_database()
        try:
            self._storage = AutoStorage[Document](self.collection)
        except Exception:
            raise TimeoutError("storage connection error")
        try:
            self._vectorstore = AutoVectorStore[DocIndex](self.collection)
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
        
    @abstractmethod
    def insert(self):
        r"""
        read, split and embed files
        """
        ...

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
