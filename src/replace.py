import gradio as gr
from cardinal import AutoVectorStore, AutoStorage
from types import DocIndex, Document
import delete, insert


# for test
storage = AutoStorage[Document](name='test')
vectorstore = AutoVectorStore[DocIndex](name='test')
#def replace(storage:AutoStorage, vectorstore:AutoVectorStore, query:str, new_content:str):
def replace(query, new_content):
    delete.delete(query)
    insert.insert([new_content])


if __name__ == '__main__':
    # TODO
    gr.Interface(fn=replace, inputs=gr.Text(), outputs=gr.Text()).launch()
    