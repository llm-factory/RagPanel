import gradio as gr
from dotenv import load_dotenv


load_dotenv()


from .engine import Engine
from .components import create_database_block, create_functions_block, create_tools_block


def create_ui():
    with gr.Blocks() as demo:
        engine = Engine()
        gr.HTML("<center><h1>RAG Panel</h1></center>")
        search_result_state = gr.State()
        
        # tools
        gr.HTML("<b>configure your tools")
        create_tools_block(engine)
            
        # database
        gr.HTML("<b>choose your database</b>")
        create_database_block(engine)
        
        # functions
        create_functions_block(engine, search_result_state)
    return demo
