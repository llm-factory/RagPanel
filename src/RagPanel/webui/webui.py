import gradio as gr
from dotenv import load_dotenv


load_dotenv()

from ..utils import init_env
init_env()

from ..engines import UiEngine
from .components import create_database_block, create_functions_block, create_tools_block


def create_ui(lang):
    from ..utils.locales import LOCALES
    LOCALES = {key: value[lang] for key, value in LOCALES.items()}
    with gr.Blocks() as demo:
        engine = UiEngine(LOCALES)
        gr.HTML("<center><h1>RAG Panel</h1></center>")
        search_result_state = gr.State()

        # database
        gr.HTML(f"<b>{LOCALES['Database_Environment']}</b>")
        create_database_block(engine, LOCALES)

        # tools
        gr.HTML(f"<b>{LOCALES['Tools_Environment']}")
        create_tools_block(engine, LOCALES)

        # functions
        create_functions_block(engine, search_result_state, LOCALES)
    return demo
