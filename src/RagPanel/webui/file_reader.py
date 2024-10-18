import os
import gradio as gr
from .protocol import Text, CSV


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
    

def read_word(filepath, is_doc):
    try:
        from docx import Document
    except ImportError:
        print("please install python-docx with 'pip install python-docx' to read .docx files")
        raise
    
    if is_doc: #TODO: change to .docx first
        pass
    
    doc = Document(filepath)
    contents = "\n".join(para.text for para in doc.paragraphs)
    return Text(filepath, contents)


def read_pdf(filepath):
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        print("please install pdfminer.six with 'pip install pdfminer.six' to read .pdf files")
        raise

    contents = extract_text(filepath)
    return Text(filepath, contents)

def read_file(filepath):
    # input is list
    if isinstance(filepath, list):
        progress = gr.Progress()
        progress(0, "start to load files")
        files = []
        for f in progress.tqdm(filepath, desc="load files"):
            files.extend(read_file(f))
        return files

    # supported types: .txt, .json, .docx, .doc, .pdf, .csv
    _, extension = os.path.splitext(filepath)
    extension = extension.lower()
    if extension == '.txt':
        return [read_txt(filepath)]

    elif extension == '.csv':
        return [read_csv(filepath)]
    
    elif extension == '.json':
        return [read_json(filepath)]
    
    elif extension == '.docx' or extension == '.doc':
        return [read_word(filepath, extension=='.doc')]
    
    elif extension == '.pdf':
        return [read_pdf(filepath)]

    else:
        raise gr.Error(f"unsupported file type: {extension}")
    

def split(file, splitter):
    if isinstance(file, CSV):
        ret = []
        for key, content in zip(file.keys, file.contents):
            chunks = splitter.split(content)
            for chunk in chunks:
                ret.append({"content": chunk, "key": key, "path": file.filepath})
        return ret

    elif isinstance(file, Text):
        ret = []
        chunks = splitter.split(file.contents)
        for chunk in chunks:
            ret.append({"content": chunk, "key": None, "path": file.filepath})
        return ret
