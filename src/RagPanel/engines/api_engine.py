from tqdm import tqdm
from multiprocessing import Pool
from functools import partial
from cardinal import get_logger, CJKTextSplitter
from .engine import BaseEngine
from ..utils.file_reader import read_folder, split
from ..utils.protocol import DocIndex, Document


class ApiEngine(BaseEngine):
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        
    def insert(self, folder, num_proc):
        self.check_database()
        if self._splitter is None:
            print("loading splitter...")
            self._splitter = CJKTextSplitter()
        file_contents = read_folder(folder)
        text_chunks = []
        partial_split = partial(split, self._splitter)
        with Pool(processes=num_proc) as pool:
            for chunks in tqdm(
                pool.imap_unordered(partial_split, file_contents),
                total=len(file_contents),
                desc="split content",
            ):
                text_chunks.extend(chunks)

        BATCH_SIZE=1000
        bar = tqdm(total=len(text_chunks), desc="build index")
        for i in range(0, len(text_chunks), BATCH_SIZE):
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
                bar.update(1)
            self._vectorstore.insert(texts, batch_index)
            self._storage.insert(batch_ids, batch_document)

        self.logger.info("Build completed.")
