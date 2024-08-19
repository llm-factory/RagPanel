import gradio as gr
from .splitter import create_splitter_tab


def create_tools_block(engine):
    with gr.Blocks() as demo:
        with gr.Tab("Splitter"):
            create_splitter_tab(engine)
    return demo