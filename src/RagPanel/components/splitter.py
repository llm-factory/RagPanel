import os
import gradio as gr


def create_splitter_tab(engine):
    with gr.Row() as demo:
        path = gr.Textbox(label="splitter path", info="path of your splitter (from hugging face or local), use tiktoken if empty", value=os.environ['HF_TOKENIZER_PATH'], scale=3)
        chunk_size = gr.Number(value=os.environ['DEFAULT_CHUNK_SIZE'], step=50, label="chunk size", info="the max size of each document chunk", scale=2)
        chunk_overlap = gr.Number(value=os.environ['DEFAULT_CHUNK_OVERLAP'], step=10, label="chunk overlap", info="the size of overlap between document chunks", scale=2)
        confirm_button = gr.Button("confirm")
    confirm_button.click(engine.set_splitter, [path, chunk_size, chunk_overlap])
    return demo
