import gradio as gr
from cardinal import AutoVectorStore, AutoStorage
from types import DocIndex, Document


# for test
storage = AutoStorage[Document](name='test')
vectorstore = AutoVectorStore[DocIndex](name='test')
#def search(storage:AutoStorage, vectorstore:AutoVectorStore, query:str):
def search(query):
    index = vectorstore.search(query=query, top_k=1)[0][0]
    doc = storage.query(key=index.doc_id)
    return doc.content


if __name__ == '__main__':
    gr.Interface(fn=search, inputs=gr.Text(), outputs=gr.Text()).launch()
    