import gradio as gr
from ...save_env import save_as_dotenv
from ..tools.splitter import create_splitter_tab
from ..tools.model import create_model_tab


def create_tools_block(engine):
    with gr.Blocks() as demo:
        with gr.Tab("Splitter"):
            create_splitter_tab()
        with gr.Tab("Model"):
            create_model_tab()
        save_env_button = gr.Button("save env")
    save_env_button.click(save_as_dotenv)
    save_env_button.click(engine.set_tools)
    return demo
