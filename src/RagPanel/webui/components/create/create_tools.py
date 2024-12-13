import gradio as gr
from ....utils import save_as_dotenv
from ..tools import create_splitter_tab,create_model_tab, create_retrieve_tab


def create_tools_block(engine, LOCALES):
    with gr.Blocks() as demo:
        with gr.Tab(LOCALES["Splitter"]):
            create_splitter_tab(LOCALES)
        with gr.Tab(LOCALES["Model"]):
            create_model_tab(LOCALES)
        with gr.Tab(LOCALES["Retrieve"]):
            create_retrieve_tab(engine, LOCALES)
        save_env_button = gr.Button(LOCALES["apply_and_save"])
    save_env_button.click(save_as_dotenv)
    save_env_button.click(engine.update_tools)
    save_env_button.click(gr.Info, gr.State(LOCALES["configuration_applied"]))
    return demo
