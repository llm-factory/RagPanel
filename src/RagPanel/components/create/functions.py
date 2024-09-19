import gradio as gr
from ...chat_engine import ChatEngine
from ..functions.chat import create_chat_tab
from ..functions.insert import create_insert_tab
from ..functions.delete import create_delete_tab
from ..functions.search_delete import create_search_delete_tab


def create_functions_block(engine, search_result_state):
    chat_engine = ChatEngine("init", engine)
    with gr.Blocks() as demo:
        gr.HTML("<b>insert, search and delete</b>")
        with gr.Tab("Insert"):
            create_insert_tab(engine)
        with gr.Tab("Search"):
            create_search_delete_tab(engine, search_result_state)
        with gr.Tab("Delete"):
            create_delete_tab(engine)
        with gr.Tab("Chat"):
            create_chat_tab(chat_engine)
    return demo
