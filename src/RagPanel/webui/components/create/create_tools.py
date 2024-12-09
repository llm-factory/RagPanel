import gradio as gr
from ....utils import save_as_dotenv
from ..tools import create_splitter_tab,create_model_tab, create_retriever_tab


def create_tools_block(engine, LOCALES):
    with gr.Blocks() as demo:
        threshold = gr.State(1.0)
        top_k = gr.State(5)
        with gr.Tab(LOCALES["Splitter"]):
            create_splitter_tab(LOCALES)
        with gr.Tab(LOCALES["Model"]):
            create_model_tab(LOCALES)
        with gr.Tab(LOCALES["Retriever"]):
            create_retriever_tab(threshold, top_k, LOCALES)
        save_env_button = gr.Button(LOCALES["apply_and_save"])
    save_env_button.click(save_as_dotenv)
    save_env_button.click(engine.update_tools, [threshold, top_k])
    save_env_button.click(gr.Info, gr.State(LOCALES["configuration_applied"]))
    return demo
