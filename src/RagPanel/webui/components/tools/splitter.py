import os
import gradio as gr
from ....utils import save_to_env


def create_splitter_tab(LOCALES):
    with gr.Blocks() as demo:
        with gr.Row():
            path = gr.Textbox(info=LOCALES["tokenizer_info"],
                              value=os.getenv('HF_TOKENIZER_PATH'),
                              label=LOCALES["tokenizer"],
                              scale=3)
            path.change(save_to_env, [gr.State("HF_TOKENIZER_PATH"), path])
            chunk_size = gr.Number(value=os.getenv('DEFAULT_CHUNK_SIZE'),
                                   label=LOCALES["chunk_size"],
                                   step=50,
                                   scale=2)
            chunk_size.change(save_to_env, [gr.State("DEFAULT_CHUNK_SIZE"), chunk_size])
            chunk_overlap = gr.Number(value=os.getenv('DEFAULT_CHUNK_OVERLAP'),
                                      label=LOCALES["chunk_overlap"],
                                      step=10, 
                                      scale=2)
            chunk_overlap.change(save_to_env, [gr.State("DEFAULT_CHUNK_OVERLAP"), chunk_overlap])

    return demo
    