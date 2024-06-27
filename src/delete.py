import gradio as gr
from cardinal import AutoVectorStore, AutoStorage, AutoCondition
from types import DocIndex, Document, Operator


# for test
storage = AutoStorage[Document](name='test')
vectorstore = AutoVectorStore[DocIndex](name='test')
#def delete(storage:AutoStorage, vectorstore:AutoVectorStore, query:str):
def delete(query):
    key = vectorstore.search(query=query, top_k=1)[0][0]
    storage.delete(key=key.doc_id)
    vectorstore.delete(AutoCondition(key="doc_id", value=key.doc_id, op=Operator.Eq))
    
if __name__ == '__main__':
    gr.Interface(fn=delete, inputs=gr.Text(), outputs=gr.Text()).launch()
    