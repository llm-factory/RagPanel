import csv
import pandas as pd
import gradio as gr
from dotenv import load_dotenv


load_dotenv() # must before cardinal


from cardinal import AutoStorage, AutoVectorStore, CJKTextSplitter, AutoCondition
from .typing import DocIndex, Document, Text, CSV, Operator


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
        progress = gr.Progress()
        progress(0, "start to load files")
        files = []
        for f in progress.tqdm(filepath, desc="load files"):
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
        """init database"""
        # TODO: 读取已经存在的database
        self.splitter = None
        self.cur_name = None
        self.cur_storage = None
        self.cur_vectorstore = None

    def create_database(self, name):
        self.cur_name = name
        self.cur_storage = AutoStorage[Document](name)
        self.cur_vectorstore = AutoVectorStore[DocIndex](name)

    def clear_database(self):
        self.destroy_database()
        self.create_database(self.cur_name)

    def destroy_database(self):
        self.cur_storage.destroy()
        self.cur_vectorstore.destroy()
        self.cur_storage = None
        self.cur_vectorstore = None

    def check_database(self):
        if self.cur_storage is None:
            gr.Info("Please create a database first")
            # TODO: 定义error
            raise ValueError

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

    # TODO: 修改合适逻辑
    # def replace(self, query, new_content):
    #     self.delete(query, 1)
    #     self.insert(new_content, 1)
    #     return 'replaced successfully'

    def search(self, query, threshold, top_k):
        self.check_database()
        try:
            index = self.cur_vectorstore.search(query=query, top_k=top_k)
        except ValueError:
            return pd.DataFrame([])
        docs = []
        for i in range(min(top_k, len(index))):
            score = index[i][1]
            if score < threshold:
                break
            doc_id = index[i][0].doc_id
            doc = self.cur_storage.query(key=doc_id).content
            docs.append({"id": doc_id, "content": doc})
        if len(docs) < top_k:
            gr.Info("No enough candidates")
        return pd.DataFrame(docs)
