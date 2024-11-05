import gradio as gr
from dotenv import load_dotenv


load_dotenv()


from ..engines import UiEngine
from .components import create_database_block, create_functions_block, create_tools_block


def create_ui():
    with gr.Blocks() as demo:
        engine = UiEngine()
        gr.HTML("<center><h1>RAG Panel</h1></center>")
        search_result_state = gr.State()
        
        # database
        gr.HTML("<b>configure your database</b>")
        create_database_block(engine)

        # tools
        gr.HTML("<b>configure your tools")
        create_tools_block(engine)
        
        # functions
        create_functions_block(engine, search_result_state)
    return demo
