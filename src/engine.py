import csv
from tqdm import tqdm
from multiprocessing import Pool
from cardinal import AutoStorage, AutoVectorStore, CJKTextSplitter, AutoCondition
from .filetypes import DocIndex, Document, Text, CSV, Operator


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
        

def process_file(filepath):
    file_contents = read_file(filepath)
    insert(file_contents, storage, vectorstore)
    return "inserted successfully"

def delete(query):
    key = vectorstore.search(query=query, top_k=1)[0][0]
    storage.delete(key=key.doc_id)
    vectorstore.delete(AutoCondition(key="doc_id", value=key.doc_id, op=Operator.Eq))
    return f"doc - {key.doc_id} deleted"

def replace(query, new_content):
    delete(query)
    insert([new_content])
    return 'replaced successfully'

def search(query):
    index = vectorstore.search(query=query, top_k=1)[0][0]
    doc = storage.query(key=index.doc_id)
    return doc.content