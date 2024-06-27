import gradio as gr
from tqdm import tqdm
from multiprocessing import Pool
import csv
from cardinal import CJKTextSplitter, AutoStorage, AutoVectorStore
from types import Text, CSV, DocIndex, Document


# for test
storage = AutoStorage[Document](name='test')
vectorstore = AutoVectorStore[DocIndex](name='test')

def read_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return Text(filepath, f.read())

def read_csv(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        # regard 1st col as key and 2nd col as value
        return CSV(filepath, {row[0]: row[1] for row in reader})

def read_file(filepath):
    # input is list
    if isinstance(filepath, list):
        files = []
        for f in tqdm(filepath, desc="load files"):
            files.extend(read_file(f))
        return files
    
    # only .txt or .csv suppoted
    if filepath.endswith('.txt'):
        return [read_txt(filepath).content]
    
    elif filepath.endswith('.csv'):
        return [read_csv(filepath).content]
    
    else:
        raise NotImplementedError
    
def insert(file_contents: list[str], storage, vectorstore):
    splitter = CJKTextSplitter()
    text_chunks = []
    with Pool(processes=32) as pool:
        for chunks in tqdm(
            pool.imap_unordered(splitter.split, file_contents),
            total=len(file_contents),
            desc="split files"
        ):
            text_chunks.extend(chunks)
    BATCH_SIZE=1000
    for i in tqdm(range(0, len(text_chunks), BATCH_SIZE), desc="build index"):
        batch_text = text_chunks[i : i + BATCH_SIZE]
        batch_index, batch_ids, batch_document = [], [], []
        for text in batch_text:
            index = DocIndex()
            print(index.doc_id)
            document = Document(doc_id=index.doc_id, content=text)
            batch_ids.append(index.doc_id)
            batch_index.append(index)
            batch_document.append(document)
        vectorstore.insert(batch_text, batch_index)
        storage.insert(batch_ids, batch_document)
        
#def process_file(filepath, storage:AutoStorage, vectorstore:AutoVectorStore):
def process_file(filepath):
    file_contents = read_file(filepath)
    insert(file_contents, storage, vectorstore)
    # TODO: proper return
    
if __name__ == '__main__':
    gr_insert = gr.File(type="filepath", file_count="multiple", file_types=["txt", "csv"])
    gr.Interface(fn=process_file, inputs=gr_insert, outputs=gr.Text()).launch()
    