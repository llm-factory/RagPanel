import os
import gradio as gr
from ..info import info_set_success


def create_model_tab(engine):
    with gr.Blocks() as demo:
        with gr.Row():
            url = gr.Textbox(label="openai base url",
                             info="base url of openai model or imitater",
                             value=os.getenv('OPENAI_BASE_URL', "http://localhost:8000/v1"))
            api = gr.Textbox(label="openai api key",
                             info="api key of openai model or imitater",
                             value=os.getenv('OPENAI_API_KEY', "0"))
        with gr.Row():
            chat_model = gr.Textbox(label="chat model",
                                    info="chat model name",
                                    value=os.getenv('DEFAULT_CHAT_MODEL', "gpt-4o-mini"),
                                    scale=3)
            embed_model = gr.Textbox(label="embed model",
                                     info="embedding model name",
                                     value=os.getenv('DEFAULT_EMBED_MODEL', "text-embedding-ada-002"),
                                     scale=3)
            confirm_button = gr.Button("apply")
    confirm_button.click(engine.set_model, [url, api, chat_model, embed_model]).success(info_set_success)
    return demo
