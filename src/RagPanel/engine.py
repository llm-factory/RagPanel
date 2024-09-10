import os
import pandas as pd
import gradio as gr
from .save_env import save_to_env, save_storage_path, save_vectorstore_path
from .doc_types import DocIndex, Document, Text, CSV, Operator
from cardinal import AutoStorage, AutoVectorStore, CJKTextSplitter, AutoCondition, DenseRetriever


def split(file, splitter):
    if isinstance(file, CSV):
        ret = []
        for key, content in zip(file.keys, file.contents):
            chunks = splitter.split(content)
            for chunk in chunks:
                ret.append({"content": chunk, "key": key})
        return ret

    elif isinstance(file, Text):
        ret = []
        chunks = splitter.split(file.contents)
        for chunk in chunks:
            ret.append({"content": chunk, "key": None})
        return ret


def read_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return Text(filepath, f.read())


def read_csv(filepath):
    import csv
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        # regard 1st col as key and 2nd col as value
        keys = []
        contents = []
        for row in reader:
            keys.append(row[0])
            contents.append(row[1])
        return CSV(filepath, keys, contents)
    

def read_json(filepath):
    import json
    with open(filepath, "r", encoding='utf-8') as f:
        jsons = json.load(f)
        keys = jsons.keys()
        contents = jsons.values()
        contents = [str(content) for content in contents]
        return CSV(filepath, keys, contents)


def read_file(filepath):
    # input is list
    if isinstance(filepath, list):
        progress = gr.Progress()
        progress(0, "start to load files")
        files = []
        for f in progress.tqdm(filepath, desc="load files"):
            files.extend(read_file(f))
        return files

    # only .txt or .csv suppoted
    _, extension = os.path.splitext(filepath)
    extension = extension.lower()
    if extension == '.txt':
        return [read_txt(filepath)]

    elif extension == '.csv':
        return [read_csv(filepath)]
    
    elif extension == '.json':
        return [read_json(filepath)]

    else:
        raise NotImplementedError


class Engine:
    def __init__(self):
        """init database"""
        self.splitter = None
        self.supported_storages = [
            "redis",
            "es"
        ]
        self.supported_vectorstores = [
            "chroma",
            "milvus"
        ]
        self.cur_storage = None
        self.cur_storage_name = None
        self.cur_vectorstore = None
        self.cur_vectorstore_name = None
        self.chat_model = None

    def set_model(self, url, api, chat_model, embed_model):
        save_to_env("OPENAI_BASE_URL", url)
        save_to_env("OPENAI_API_KEY", api)
        save_to_env("DEFAULT_CHAT_MODEL", chat_model)
        save_to_env("DEFAULT_EMBED_MODEL", embed_model)
        from cardinal.model.config import settings
        settings.default_chat_model = chat_model
        settings.default_embed_model = embed_model

    def set_splitter(self, path, chunk_size, chunk_overlap):
        chunk_size = int(chunk_size)
        chunk_overlap = int(chunk_overlap)
        save_to_env("HF_TOKENIZER_PATH", path)
        save_to_env("DEFAULT_CHUNK_SIZE", chunk_size)
        save_to_env("DEFAULT_CHUNK_OVERLAP", chunk_overlap)
        from cardinal.model.config import settings
        settings.hf_tokenizer_path = path
        self.splitter = CJKTextSplitter(chunk_size, chunk_overlap)

    def create_database(self, storage, storage_path, storage_name, vectorstore, vectorestore_path, vectorstore_name, vectorstore_token):
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
        files = read_file(filepath)
        self.insert_to_store(files, num_proc)
        return "insertion finished"

    def delete(self, ids, docs):
        for doc_id in ids:
            self.delete_by_id(doc_id)

        docs = docs[~docs["id"].isin(ids)]
        if len(ids) == 1:
            gr.Info("1 file is deleted")
        elif len(ids) > 1:
            gr.Info(f"{len(ids)} files are deleted")
        return docs

    def delete_by_id(self, id):
        self.cur_storage.delete(key=id)
        self.cur_vectorstore.delete(AutoCondition(key="doc_id", value=id, op=Operator.Eq))

    def search(self, query, threshold, top_k):
        self.check_database()
        try:
            retriever = DenseRetriever[DocIndex](vectorstore_name=self.cur_vectorstore_name, threshold=threshold)
            doc_indexes = retriever.retrieve(query=query, top_k=top_k)
        except ValueError:
            return pd.DataFrame([])
        docs = []
        for index in doc_indexes:
            doc_id = index.doc_id
            doc = self.cur_storage.query(key=doc_id).content
            docs.append({"id": doc_id, "content": doc})
        if len(docs) < top_k:
            gr.Warning("No enough candidates")
        return pd.DataFrame(docs)
