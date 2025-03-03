import os
from tqdm import tqdm
from .protocol import Text, CSV
import json
import csv
import docx2txt
from pdfminer.high_level import extract_text
import tempfile
import shutil


def read_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return Text(filepath, f.read())


def read_csv(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        keys = []
        contents = []
        for row in reader:
            if len(row) >= 2:  # 确保至少有两列
                keys.append(row[0])
                contents.append(row[1])
        return CSV(filepath, keys, contents)


def read_json(filepath):
    with open(filepath, "r", encoding='utf-8') as f:
        jsons = json.load(f)
        keys = list(jsons.keys())
        contents = [str(content) for content in jsons.values()]
        return CSV(filepath, keys, contents)


def read_word(filepath):
    text = docx2txt.process(filepath)
    return Text(filepath, text)


def read_pdf(filepath):
    contents = extract_text(filepath)
    return Text(filepath, contents)


def read_file(filepath):
    # supported types: .txt, .json, .docx, .doc, .pdf, .csv
    _, extension = os.path.splitext(filepath)
    extension = extension.lower()
    
    file_handlers = {
        '.txt': read_txt,
        '.csv': read_csv,
        '.json': read_json,
        '.docx': read_word,
        '.doc': read_word,
        '.pdf': read_pdf
    }
    
    handler = file_handlers.get(extension)
    if handler is None:
        raise NotImplementedError(f"不支持的文件类型: {extension}")
    
    return handler(filepath)


def read_folder(folder):
    input_files = []
    for path in folder.rglob("*.*"):
        if path.is_file():
            input_files.append(path)
    contents = []
    for file in tqdm(input_files, desc="Extract content"):
        contents.extend(read_file(file))
    return contents


def split(splitter, file):
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
