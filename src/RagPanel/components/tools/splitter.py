import os
import gradio as gr
from ..info import info_set_success


def create_splitter_tab(engine):
    with gr.Row() as demo:
        path = gr.Textbox(label="splitter path", info="path of your splitter (from hugging face or local), use tiktoken if empty", value=os.getenv('HF_TOKENIZER_PATH', "01-ai/Yi-6B-Chat"), scale=3)
        chunk_size = gr.Number(value=os.getenv('DEFAULT_CHUNK_SIZE', "300"), step=50, label="chunk size", info="the max size of each document chunk", scale=2)
        chunk_overlap = gr.Number(value=os.getenv('DEFAULT_CHUNK_OVERLAP', "30"), step=10, label="chunk overlap", info="the size of overlap between document chunks", scale=2)
        confirm_button = gr.Button("apply")
    confirm_button.click(engine.set_splitter, [path, chunk_size, chunk_overlap]).success(info_set_success)
    return demo
    