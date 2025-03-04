import gradio as gr
from ..functions import create_chat_tab, create_delete_tab, create_insert_tab, create_search_delete_tab


def create_functions_block(engine, search_result_state, LOCALES):
    with gr.Blocks() as demo:
        with gr.Tab(LOCALES["Chat"]):
            create_chat_tab(engine, LOCALES)
        with gr.Tab(LOCALES["Insert"]):
            create_insert_tab(engine, LOCALES)
        with gr.Tab(LOCALES["Search"]):
            create_search_delete_tab(engine, search_result_state, LOCALES)
        with gr.Tab(LOCALES["Delete"]):
            create_delete_tab(engine, LOCALES)
    return demo
