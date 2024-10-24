import os
import gradio as gr
from ....utils import save_to_env


def create_model_tab():
    with gr.Blocks() as demo:
        with gr.Row():
            url = gr.Textbox(label="openai base url",
                             info="base url of openai model or imitater",
                             value=os.getenv('OPENAI_BASE_URL', "http://localhost:8000/v1"))
            url.change(save_to_env, [gr.State("OPENAI_BASE_URL"), url])
            api = gr.Textbox(label="openai api key",
                             info="api key of openai model or imitater",
                             value=os.getenv('OPENAI_API_KEY', "0"))
            api.change(save_to_env, [gr.State("OPENAI_API_KEY"), api])
        with gr.Row():
            chat_model = gr.Textbox(label="chat model",
                                    info="chat model name",
                                    value=os.getenv('DEFAULT_CHAT_MODEL', "gpt-4o-mini"),
                                    scale=3)
            chat_model.change(save_to_env, [gr.State("DEFAULT_CHAT_MODEL"), chat_model])
            embed_model = gr.Textbox(label="embed model",
                                     info="embedding model name",
                                     value=os.getenv('DEFAULT_EMBED_MODEL', "text-embedding-ada-002"),
                                     scale=3)
            embed_model.change(save_to_env, [gr.State("DEFAULT_EMBED_MODEL"), embed_model])
    return demo
