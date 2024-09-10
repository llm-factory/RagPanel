import gradio as gr
from ..functions.insert import create_insert_tab
from ..functions.search_delete import create_search_delete_tab


def create_functions_block(engine, search_result_state):
    with gr.Blocks() as demo:
        gr.HTML("<b>insert, search and delete</b>")
        with gr.Tab("Insert"):
            create_insert_tab(engine)
        with gr.Tab("Search&Delete"):
            create_search_delete_tab(engine, search_result_state)
#        with gr.Tab("Chat"):
#            create_chat_tab(engine)
    return demo
