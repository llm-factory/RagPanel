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
        
def insert(files):
    text_chunks = []
    with Pool(processes=32) as pool:
        for chunks in tqdm(
            pool.imap_unordered(split, files),
            total=len(files),
            desc="split files"
        ):
            text_chunks.extend(chunks)
    BATCH_SIZE=1000
    for i in tqdm(range(0, len(text_chunks), BATCH_SIZE), desc="build index"):
        batch_text = text_chunks[i : i + BATCH_SIZE]
        texts, batch_index, batch_ids, batch_document = [], [], [], []
        for text in batch_text:
            index = DocIndex()
            if text["key"] is None:
                texts.append(text)
            else:
                texts.append(text["key"])
            document = Document(doc_id=index.doc_id, content=text["content"])
            batch_ids.append(index.doc_id)
            batch_index.append(index)
            batch_document.append(document)
        vectorstore.insert(texts, batch_index)
        storage.insert(batch_ids, batch_document)

def process_file(filepath):
    files = read_file(filepath)
    insert(files)
    return "inserted successfully"

def delete(query, top_k):
    keys = vectorstore.search(query=query, top_k=top_k)
    ret = ""
    for i in range(top_k):
        doc_id = keys[i][0].doc_id
        storage.delete(key=doc_id)
        vectorstore.delete(AutoCondition(key="doc_id", value=doc_id, op=Operator.Eq))
        ret += f"doc-{doc_id}\n"
    return "Following docs are deleted:\n" + ret

def replace(query, new_content):
    delete(query, 1)
    insert([new_content])
    return 'replaced successfully'

def search(query, top_k):
    index = vectorstore.search(query=query, top_k=top_k)
    docs = []
    for i in range(top_k):
        doc_id = index[i][0].doc_id
        doc = storage.query(key=doc_id).content
        docs.append(doc)
    return docs