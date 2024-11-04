import os
import pandas as pd
import gradio as gr
from .file_reader import read_file, split
from .protocol import DocIndex, Document, Operator
from .save_env import save_to_env, save_storage_path, save_vectorstore_path
from cardinal import AutoStorage, AutoVectorStore, CJKTextSplitter, AutoCondition, DenseRetriever


class Engine:
    def __init__(self):
        self.splitter = None
        self.cur_storage = None
        self.cur_storage_name = None
        self.cur_vectorstore = None
        self.cur_vectorstore_name = None
        self.file_history = []
        self.file_chunk_map = {}
        self.supported_storages = [
            "redis",
            "es"
        ]
        self.supported_vectorstores = [
            "chroma",
            "milvus"
        ]
        
    def set_tools(self):
        from cardinal.model.config import settings
        settings.default_chat_model = os.getenv("DEFAULT_CHAT_MODEL")
        settings.default_embed_model = os.getenv("DEFAULT_EMBED_MODEL")
        settings.hf_tokenizer_path = os.getenv("HF_TOKENIZER_PATH")
        self.splitter = CJKTextSplitter(int(os.getenv("DEFAULT_CHUNK_SIZE")),
                                        int(os.getenv("DEFAULT_CHUNK_OVERLAP")))
        
    def create_database(self, storage_name, vectorstore_name):
        self.cur_storage = AutoStorage[Document](storage_name)
        self.cur_storage_name = storage_name
        self.cur_vectorstore = AutoVectorStore[DocIndex](vectorstore_name)
        self.cur_vectorstore_name = vectorstore_name


    def create_database_ui(self, storage, storage_path, storage_name, vectorstore, vectorestore_path, vectorstore_name, vectorstore_token):
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
            self.cur_storage = AutoStorage[Document](storage_name)
            self.cur_storage_name = storage_name
        except NameError:
            raise gr.Error("Please install dependencies according to your database")
        except Exception:
            raise gr.Error("storage connection error")
        try:
            self.cur_vectorstore = AutoVectorStore[DocIndex](vectorstore_name)
            self.cur_vectorstore_name = vectorstore_name
        except Exception:
            raise gr.Error("vectorstore connection error")

    def clear_database(self):
        self.check_database()
        self.destroy_database()
        try:
            self.cur_storage = AutoStorage[Document](self.cur_storage_name)
        except Exception:
            raise gr.Error("storage connection error")
        try:
            self.cur_vectorstore = AutoVectorStore[DocIndex](self.cur_vectorstore_name)
        except Exception:
            raise gr.Error("vectorstore connection error")

    def destroy_database(self):
        self.check_database()
        if not self.cur_storage.exists():
            self.cur_storage = None
            self.cur_vectorstore = None
            return
        self.cur_storage.destroy()
        self.cur_vectorstore.destroy()
        self.cur_storage = None
        self.cur_vectorstore = None

    def check_database(self):
        if self.cur_storage is None:
            raise gr.Error("Please create a database first")

    def insert_to_store(self, files, num_proc): #TODO:结合多线程与gr.Process
        if self.splitter is None:
            progress = gr.Progress()
            progress(0, "start to load splitter")
            for i in progress.tqdm(range(1), desc="loading splitter"):
                self.splitter = CJKTextSplitter()
        text_chunks = []
        progress = gr.Progress()
        progress(0, "start to split files")
        for chunks in progress.tqdm(
            files,
            desc="split files"
        ):
            text_chunks.extend(split(chunks, self.splitter))
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
            self.cur_vectorstore.insert(texts, batch_index)
            self.cur_storage.insert(batch_ids, batch_document)

    def insert(self, filepath, num_proc):
        self.check_database()
        self.file_history.extend(filepath)
        files = read_file(filepath)
        self.insert_to_store(files, num_proc)
        return "insertion finished"

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
        self.cur_storage.delete(key=id)
        self.cur_vectorstore.delete(AutoCondition(key="doc_id", value=id, op=Operator.Eq))

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

    def search(self, query, threshold, top_k):
        self.check_database()
        try:
            retriever = DenseRetriever[DocIndex](vectorstore_name=self.cur_vectorstore_name, threshold=threshold)
            doc_indexes = retriever.retrieve(query=query, top_k=top_k)
        except:
            return pd.DataFrame([])
        docs = []
        for index in doc_indexes:
            doc_id = index.doc_id
            doc = self.cur_storage.query(key=doc_id).content
            docs.append({"id": doc_id, "content": doc})
        if len(docs) < top_k:
            gr.Warning("No enough candidates")
        return pd.DataFrame(docs)
