import csv
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
from dotenv import load_dotenv


load_dotenv() # must before cardinal


from cardinal import AutoStorage, AutoVectorStore, CJKTextSplitter, AutoCondition
from .typing import DocIndex, Document, Text, CSV, Operator


def split(file):
    splitter = CJKTextSplitter()
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
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        # regard 1st col as key and 2nd col as value
        keys = []
        contents = []
        for row in reader:
            keys.append(row[0])
            contents.append(row[1])
        return CSV(filepath, keys, contents)


def read_file(filepath):
    # input is list
    if isinstance(filepath, list):
        files = []
        for f in tqdm(filepath, desc="load files"):
            files.extend(read_file(f))
        return files

    # only .txt or .csv suppoted
    if filepath.endswith('.txt'):
        return [read_txt(filepath)]

    elif filepath.endswith('.csv'):
        return [read_csv(filepath)]

    else:
        raise NotImplementedError


def launch_rag(config, action):
    import subprocess
    command = ["python", "api_demo/launch.py", "--config", config, "--action", action]
    subprocess.Popen(command)


class Engine:
    def __init__(self):
        """初始化存储"""
        self.store_names = []
        self.storages = {}
        self.vectorstores = {}
        self.store_names.append('init')
        self.cur_storage = AutoStorage[Document](name='init')
        self.cur_vectorstore = AutoVectorStore[DocIndex](name='init')
        self.storages.update({'init': self.cur_storage})
        self.vectorstores.update({'init': self.cur_vectorstore})

    def new_store(self, name):
        self.store_names.append(name)
        self.storages.update({name: AutoStorage[Document](name)})
        self.vectorstores.update({name: AutoVectorStore[DocIndex](name)})

    def change_to(self, name):
        self.cur_storage = self.storages[name]
        self.cur_vectorstore = self.vectorstores[name]

    def rm_store(self, name):
        self.store_names.remove(name)
        storage = self.storages[name]
        storage.destroy()
        vectorestore = self.vectorstores[name]
        vectorestore.destroy()
        if self.cur_vectorstore.name == name:
            self.cur_vectorstore = None
            self.cur_storage = None

    def destroy(self):
        for name in self.store_names:
            self.rm_store(name)

    def insert_to_store(self, files):
        text_chunks = []
        with Pool(processes=32) as pool:
            for chunks in tqdm(
                    pool.imap_unordered(split, files),
                    total=len(files),
                    desc="split files"
            ):
                text_chunks.extend(chunks)
        BATCH_SIZE = 1000
        for i in tqdm(range(0, len(text_chunks), BATCH_SIZE), desc="build index"):
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

    def insert(self, filepath):
        files = read_file(filepath)
        self.insert_to_store(files)
        return "inserted successfully"

    def delete(self, query, top_k):
        keys = self.cur_vectorstore.search(query=query, top_k=top_k)
        ret = ""
        for i in range(top_k):
            doc_id = keys[i][0].doc_id
            self.cur_storage.delete(key=doc_id)
            self.cur_vectorstore.delete(AutoCondition(key="doc_id", value=doc_id, op=Operator.Eq))
            ret += f"doc-{doc_id}\n"
        return "Following docs are deleted:\n" + ret

    def delete_by_id(self, id):
        self.cur_storage.delete(key=id)
        self.cur_vectorstore.delete(AutoCondition(key="doc_id", value=id, op=Operator.Eq))

    def replace(self, query, new_content):
        self.delete(query, 1)
        self.insert(new_content)
        return 'replaced successfully'

    def search(self, query, top_k):
        index = self.cur_vectorstore.search(query=query, top_k=top_k)
        docs = []
        for i in range(top_k):
            doc_id = index[i][0].doc_id
            doc = self.cur_storage.query(key=doc_id).content
            docs.append({"id": doc_id, "content": doc})
        return pd.DataFrame(docs)

