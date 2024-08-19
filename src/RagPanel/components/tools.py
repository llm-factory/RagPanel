import gradio as gr
from ..save_env import save_as_dotenv
from .splitter import create_splitter_tab


def create_tools_block(engine):
    with gr.Blocks() as demo:
        with gr.Tab("Splitter"):
            create_splitter_tab(engine)
        save_config_button = gr.Button("save config")
    save_config_button.click(save_as_dotenv)
    return demo
