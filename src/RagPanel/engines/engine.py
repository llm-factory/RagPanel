from ..utils.protocol import DocIndex, Document, Operator
from cardinal import AutoStorage, AutoVectorStore, AutoCondition, DenseRetriever


class BaseEngine:
    def __init__(self):
        self._splitter = None
        self.collection = None
        self._storage = None
        self._vectorstore = None
        self._retriver = None
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
        self._retriver = DenseRetriever[DocIndex](vectorstore_name=self.collection, threshold=1.0)
        self.collection = collection
        
    def check_database(self):
        if self._storage is None or self._vectorstore is None or self._retriver is None:
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
        self.collection = None

    def delete_by_id(self, id):
        self._storage.delete(key=id)
        self._vectorstore.delete(AutoCondition(key="doc_id", value=id, op=Operator.Eq))

    def search(self, query, top_k):
        self.check_database()
        try:
            doc_indexes = self._retriever.retrieve(query=query, top_k=top_k)
        except:
            return []
        docs = []
        for index in doc_indexes:
            doc_id = index.doc_id
            doc = self._storage.query(key=doc_id).content
            docs.append({"id": doc_id, "content": doc})
        return docs

    def launch_app(self, host, port):
        from ..api.app import launch_app
        launch_app(self, host=host, port=port)
