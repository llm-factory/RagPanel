import gradio as gr
from ....utils import ChatEngine
from ..functions import create_chat_tab, create_delete_tab, create_insert_tab, create_search_delete_tab


def create_functions_block(engine, search_result_state):
    chat_engine = ChatEngine(engine)
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
