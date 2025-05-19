import os
import pandas as pd
import gradio as gr
from tqdm import tqdm
from functools import partial
from multiprocessing import Pool
from .engine import BaseEngine
from ..utils.graph_processor import GraphProcessor
from ..utils.file_reader import read_file, split
from ..utils.protocol import DocIndex, Document, Operator
from ..utils.save_config import update_config, save_config
from ..utils.save_env import *
from cardinal import AutoStorage, AutoVectorStore, CJKTextSplitter, AutoCondition, DenseRetriever, BaseCollector
from ..utils.exception import (
    DatabaseConnectionError, 
    DatabaseNotFoundError,
    DatabaseNotInitializedError,
    StorageConnectionError,
    VectorStoreConnectionError
)


class UiEngine(BaseEngine):
    def __init__(self, LOCALES, collection="init"):
        super().__init__(collection)
        self.init_cardinal()
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

    def init_cardinal(self):
        storage = os.getenv("STORAGE", "redis")
        vectorstore = os.getenv("VECTORSTORE", "chroma")
        graph_storage = os.getenv("GRAPH_STORAGE", "None")
        storage_path = get_storage_path()
        vectorstore_path, vectorstore_token = get_vectorstore_path()
        graph_storage_path = get_graph_storage_path()

        from cardinal.storage.config import settings
        settings.storage = storage
        if storage == 'redis':
            settings.redis_uri = storage_path
        elif storage == 'es':
            settings.elasticsearch_uri = storage_path

        from cardinal.vectorstore.config import settings
        settings.vectorstore = vectorstore
        if vectorstore == 'chroma':
            settings.chroma_path =  vectorstore_path
        elif vectorstore == 'milvus':
            settings.milvus_uri = vectorstore_path
            settings.milvus_token = vectorstore_token

        from cardinal.graph.config import settings
        settings.graph_storage = graph_storage
        if graph_storage == 'neo4j':
            settings.neo4j_uri = graph_storage_path

        from cardinal.model.config import settings
        settings.default_chat_model = os.getenv("DEFAULT_CHAT_MODEL")
        settings.default_embed_model = os.getenv("DEFAULT_EMBED_MODEL")
        settings.hf_tokenizer_path = os.getenv("HF_TOKENIZER_PATH")
        
    def update_tools(self):
        self.threshold = self.tmp_threshold
        self.top_k = self.tmp_top_k
        self.reranker = os.getenv("RERANKER")
        self.splitter = CJKTextSplitter(int(os.getenv("DEFAULT_CHUNK_SIZE")),
                                        int(os.getenv("DEFAULT_CHUNK_OVERLAP")))

    def apply_and_save_database(self, collection, storage, storage_path, vectorstore, vectorstore_path, vectorstore_token, graph_storage, graph_storage_path):
        self.collection = collection
        update_config("database", "collection", collection)
        save_config()
        save_to_env("STORAGE", storage)
        save_to_env("VECTORSTORE", vectorstore)
        save_to_env("GRAPH_STORAGE", graph_storage)
        save_storage_path(storage_path)
        save_vectorstore_path(vectorstore_path, vectorstore_token)
        save_graph_storage_path(graph_storage_path)
        self.init_cardinal()
        save_as_dotenv()

        try:
            super().create_database()
        except StorageConnectionError as e:
            raise gr.Error(f"{self.LOCALES['storage_connection_error']}: {str(e)}")
        except VectorStoreConnectionError as e:
            raise gr.Error(f"{self.LOCALES['vectorstore_connection_error']}: {str(e)}")
        except DatabaseConnectionError as e:
            raise gr.Error(f"{self.LOCALES['database_error']}: {str(e)}")
        
        if graph_storage != "None":
            self._graph_processor = GraphProcessor("en", 1, collection)

    def clear_database(self):
        try:
            super().clear_database()
        except (StorageConnectionError, VectorStoreConnectionError) as e:
            raise gr.Error(f"{self.LOCALES['database_connection_error']}: {str(e)}")

    def insert(self, filepath, num_proc, batch_size, progress=gr.Progress(track_tqdm=True)):
        self.check_database()
            
        self.file_history.extend(filepath)
        file_contents = []
        for path in filepath:
            file_contents.extend(read_file(path))
        if self._splitter is None:
            self._splitter = CJKTextSplitter()
        text_chunks = []
        partial_split = partial(split, self._splitter)
        bar = tqdm(total=len(file_contents), desc=self.LOCALES["split_docs"])
        with Pool(processes=num_proc) as pool:
            for chunks in pool.imap_unordered(partial_split, file_contents):
                text_chunks.extend(chunks)
                bar.update(1)
        bar.close()
        if os.getenv("RAG_METHOD") == 'graph':
            return super().graph_insert(text_chunks)
        bar = tqdm(total=len(text_chunks), desc=self.LOCALES["build_index"])
        left_bar = len(text_chunks)
        for i in range(0, len(text_chunks), batch_size):
            batch_text = text_chunks[i: i + batch_size]
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
            bar.update(min(left_bar, batch_size))
            left_bar -= batch_size
        bar.close()
        return self.LOCALES["inserted"]

    def delete(self, del_index, docs):
        doc_ids = docs['id'].tolist()
        del_ids = []
        for index in del_index:
            del_ids.append(doc_ids[index])
            self.delete_by_id(doc_ids[index])

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
        if os.getenv("RAG_METHOD") == 'graph':
            docs = super().graph_search(query, top_k=self.top_k, mode="local", threshold=self.threshold)
        else:
            docs = super().search(query=query, top_k=self.top_k, reranker=self.reranker, threshold=self.threshold)
        if len(docs) < self.top_k:
            gr.Warning(self.LOCALES["no_enough_candidates"])
        return pd.DataFrame(docs)

    def launch_app(self, host, port):
        from ..api.app import launch_app
        launch_app(self, host=host, port=port)
