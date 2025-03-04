import gradio as gr
from dotenv import load_dotenv


load_dotenv()

from ..utils import init_env
init_env()

from ..engines import UiEngine
from .components import create_database_block, create_functions_block, create_tools_block


def create_ui(lang, collection):
    from ..utils.locales import LOCALES
    LOCALES = {key: value[lang] for key, value in LOCALES.items()}
    with gr.Blocks() as demo:
        engine = UiEngine(LOCALES, collection)
        gr.HTML("<center><h1>RAG Panel</h1></center>")
        search_result_state = gr.State()

        with gr.Tabs() as tabs:
            # Main functions tab
            with gr.Tab(LOCALES["Functions"]):
                create_functions_block(engine, search_result_state, LOCALES)

            # Configuration tab
            with gr.Tab(LOCALES["Configuration"]):
                # database
                gr.HTML(f"<b>{LOCALES['Database_Environment']}</b>")
                create_database_block(engine, collection, LOCALES)

                # tools
                gr.HTML(f"<b>{LOCALES['Tools_Environment']}</b>")
                create_tools_block(engine, LOCALES)

    return demo
