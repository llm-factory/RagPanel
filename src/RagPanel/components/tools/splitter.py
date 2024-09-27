import os
import gradio as gr
from ..info import info_set_success


def create_splitter_tab(engine):
    with gr.Blocks() as demo:
        with gr.Row():
            path = gr.Textbox(info="path of your splitter (from hugging face or local), use tiktoken if empty",
                              value=os.getenv('HF_TOKENIZER_PATH', "01-ai/Yi-6B-Chat"),
                              label="splitter path",
                              scale=3)
            chunk_size = gr.Number(info="the max size of each document chunk",
                                   value=os.getenv('DEFAULT_CHUNK_SIZE', "300"),
                                   label="chunk size",
                                   step=50, 
                                   scale=2)
            chunk_overlap = gr.Number(info="the size of overlap between document chunks",
                                      value=os.getenv('DEFAULT_CHUNK_OVERLAP', "30"),
                                      label="chunk overlap",
                                      step=10, 
                                      scale=2)
            confirm_button = gr.Button("apply")
    confirm_button.click(engine.set_splitter, [path, chunk_size, chunk_overlap]).success(info_set_success)
    return demo
    