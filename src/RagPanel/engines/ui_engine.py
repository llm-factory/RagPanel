import os
import pandas as pd
import gradio as gr
from .engine import BaseEngine
from ..utils.file_reader import read_file, split
from ..utils.protocol import DocIndex, Document, Operator
from ..utils.save_env import save_to_env, save_storage_path, save_vectorstore_path
from cardinal import AutoStorage, AutoVectorStore, CJKTextSplitter, AutoCondition, DenseRetriever, BaseCollector


class UiEngine(BaseEngine):
    def __init__(self):
        super().__init__()
        self.file_history = []
        self.file_chunk_map = {}
        
    def update_tools(self):
        from cardinal.model.config import settings
        settings.default_chat_model = os.getenv("DEFAULT_CHAT_MODEL")
        settings.default_embed_model = os.getenv("DEFAULT_EMBED_MODEL")
        settings.hf_tokenizer_path = os.getenv("HF_TOKENIZER_PATH")
        self.splitter = CJKTextSplitter(int(os.getenv("DEFAULT_CHUNK_SIZE")),
                                        int(os.getenv("DEFAULT_CHUNK_OVERLAP")))

    def create_database(self, collection, storage, storage_path, vectorstore, vectorestore_path, vectorstore_token):
        # config
        save_to_env("STORAGE", storage)
        save_to_env("VECTORSTORE", vectorstore)
        from cardinal.storage.config import settings
        settings.storage = storage
        save_storage_path(storage_path, settings)
        from cardinal.vectorstore.config import settings
        settings.vectorstore = vectorstore
        save_vectorstore_path(vectorestore_path, vectorstore_token, settings)
        # create
        try:
            self._storage = AutoStorage[Document](collection)
        except NameError:
            raise gr.Error("Please install dependencies according to your database")
        except Exception:
            raise gr.Error("storage connection error")
        try:
            self._vectorstore = AutoVectorStore[DocIndex](collection)
        except Exception:
            raise gr.Error("vectorstore connection error")
        self._retriever = DenseRetriever[DocIndex](vectorstore_name=collection, threshold=1.0)
        self.chat_engine.name = "history_" + collection
        self.chat_engine.collector = BaseCollector(storage_name="history_" + collection)
        self.collection = collection

    def clear_database(self):
        try:
            super().clear_database()
        except TimeoutError:
            raise gr.Error("database connection error")

    def insert_to_store(self, files, num_proc): #TODO:结合多线程与gr.Process
        if self._splitter is None:
            progress = gr.Progress()
            progress(0, "start to load splitter")
            for i in progress.tqdm(range(1), desc="loading splitter"):
                self._splitter = CJKTextSplitter()
        text_chunks = []
        progress = gr.Progress()
        progress(0, "start to split files")
        for chunks in progress.tqdm(
            files,
            desc="split files"
        ):
            text_chunks.extend(split(self._splitter, chunks))
        BATCH_SIZE = 1000
        progress(0, "start to build index")
        for i in progress.tqdm(range(0, len(text_chunks), BATCH_SIZE), desc="build index"):
            batch_text = text_chunks[i: i + BATCH_SIZE]
            texts, batch_index, batch_ids, batch_document = [], [], [], []
            for text in batch_text:
                index = DocIndex()
                if text["path"] not in self.file_chunk_map.keys():
                    self.file_chunk_map.update({text["path"]: [index.doc_id]})
                else:
                    self.file_chunk_map[text["path"]].append(index.doc_id)
                if text["key"] is None:
                    texts.append(text["content"])
                else:
                    texts.append(text["key"])
                document = Document(doc_id=index.doc_id, content=text["content"])
                batch_ids.append(index.doc_id)
                batch_index.append(index)
                batch_document.append(document)
            self._vectorstore.insert(texts, batch_index)
            self._storage.insert(batch_ids, batch_document)

    def insert(self, filepath, num_proc):
        self.check_database()
        self.file_history.extend(filepath)
        files = []
        for path in filepath:
            files.extend(read_file(path))
        self.insert_to_store(files, num_proc)

    def delete(self, del_index, docs):
        doc_ids = docs['id'].tolist()
        del_ids = []
        for index in del_index:
            del_ids.append(doc_ids[index])

        docs = docs[~docs["id"].isin(del_ids)]
        if len(del_ids) == 1:
            gr.Info("1 chunk is deleted")
        elif len(del_ids) > 1:
            gr.Info(f"{len(del_ids)} chunks are deleted")
        return docs

    def delete_by_id(self, id):
        self._storage.delete(key=id)
        self._vectorstore.delete(AutoCondition(key="doc_id", value=id, op=Operator.Eq))

    def delete_by_file(self, del_file_indexes):
        for index in del_file_indexes:
            try:
                file_to_del = self.file_history[index]
                ids = self.file_chunk_map[file_to_del]
                for id in ids:
                    self.delete_by_id(id)
                self.file_chunk_map.pop(file_to_del)
                self.file_history.remove(file_to_del)
            except:
                gr.Warning("") # TODO

    def search(self, query, top_k, reranker, threshold):
        docs = super().search(query=query, top_k=top_k, reranker=reranker, threshold=threshold)
        if len(docs) < top_k and len(docs) != 0:
            gr.Warning("No enough candidates")
        return pd.DataFrame(docs)

    def launch_app(self, host, port):
        from ..api.app import launch_app
        launch_app(self, host=host, port=port)
