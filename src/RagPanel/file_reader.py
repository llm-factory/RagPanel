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


def read_file(filepath):
    # input is list
    if isinstance(filepath, list):
        progress = gr.Progress()
        progress(0, "start to load files")
        files = []
        for f in progress.tqdm(filepath, desc="load files"):
            files.extend(read_file(f))
        return files

    # only .txt, .json or .csv suppoted
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