import os
import pandas as pd
import gradio as gr
from .engine import BaseEngine
from ..utils.file_reader import read_file, split
from ..utils.protocol import DocIndex, Document, Operator
from ..utils.save_env import save_to_env, save_storage_path, save_vectorstore_path
from cardinal import AutoStorage, AutoVectorStore, CJKTextSplitter, AutoCondition, DenseRetriever, BaseCollector


class UiEngine(BaseEngine):
    def __init__(self, LOCALES):
        super().__init__()
        self.file_history = []
        self.file_chunk_map = {}
        self.LOCALES = LOCALES
        self.threshold = 1.0
        self.top_k = 5
        self.reranker = "None"
        self.tmp_threshold = 1.0
        self.tmp_top_k = 5
        
    def set(self, name, value):
        setattr(self, name, value)
        
    def update_tools(self):
        from cardinal.model.config import settings
        settings.default_chat_model = os.getenv("DEFAULT_CHAT_MODEL")
        settings.default_embed_model = os.getenv("DEFAULT_EMBED_MODEL")
        settings.hf_tokenizer_path = os.getenv("HF_TOKENIZER_PATH")
        self.threshold = self.tmp_threshold
        self.top_k = self.tmp_top_k
        self.reranker = os.getenv("RERANKER", "None")
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
            raise gr.Error(self.LOCALES["dep_error"])
        except Exception:
            raise gr.Error(self.LOCALES["storage_connection_error"])
        try:
            self._vectorstore = AutoVectorStore[DocIndex](collection)
        except NameError:
            raise gr.Error(self.LOCALES["dep_error"])
        except Exception:
            raise gr.Error(self.LOCALES["vectorstore_connection_error"])
        self._retriever = DenseRetriever[DocIndex](vectorstore_name=collection, threshold=1.0)
        self.chat_engine.name = "history_" + collection
        self.chat_engine.collector = BaseCollector(storage_name="history_" + collection)
        self.collection = collection

    def clear_database(self):
        try:
            super().clear_database()
        except TimeoutError:
            raise gr.Error(self.LOCALES["database_connection_error"])
        except ValueError:
            raise gr.Error(self.LOCALES["database_not_found_error"])

    def insert_to_store(self, files, num_proc): #TODO:结合多线程与gr.Process
        if self._splitter is None:
            progress = gr.Progress()
            progress(0, self.LOCALES["load_tokenizer"])
            for i in progress.tqdm(range(1), desc=self.LOCALES["loading_tokenzier"]):
                self._splitter = CJKTextSplitter()
        text_chunks = []
        progress = gr.Progress()
        progress(0, self.LOCALES["start_to_split_docs"])
        for chunks in progress.tqdm(
            files,
            desc=self.LOCALES["spliting_docs"]
        ):
            text_chunks.extend(split(self._splitter, chunks))
        BATCH_SIZE = 1000
        progress(0, self.LOCALES["start_to_build_index"])
        for i in progress.tqdm(range(0, len(text_chunks), BATCH_SIZE), desc=self.LOCALES["building_index"]):
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
            gr.Info(self.LOCALES["deleted_1"])
        elif len(del_ids) > 1:
            gr.Info(f"{len(del_ids)} {self.LOCALES['deleted_more']}")
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

    def search(self, query):
        docs = super().search(query=query, top_k=self.top_k, reranker=self.reranker, threshold=self.threshold)
        if len(docs) < self.top_k and len(docs) != 0:
            gr.Warning(self.LOCALES["no_enough_candidates"])
        return pd.DataFrame(docs)

    def launch_app(self, host, port):
        from ..api.app import launch_app
        launch_app(self, host=host, port=port)
