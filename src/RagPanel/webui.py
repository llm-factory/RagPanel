import gradio as gr
from dotenv import load_dotenv


load_dotenv()


from .engine import Engine
from .components import create_database_block, create_insert_tab, create_search_delete_tab, create_launch_rag_tab


def create_ui():
    with gr.Blocks() as demo:
        engine = Engine()
        gr.HTML("<center><h1>RAG Panel</h1></center>")
        search_result_state = gr.State()

        gr.HTML("<b>choose your database</b>")
        create_database_block(engine)
                
        gr.HTML("<b>insert, search and delete</b>")
        with gr.Tab("Insert"):
            create_insert_tab(engine)
        with gr.Tab("Search&Delete"):
            create_search_delete_tab(engine, search_result_state)
        with gr.Tab("Launch api_demo"):
            create_launch_rag_tab(engine)
    return demo
