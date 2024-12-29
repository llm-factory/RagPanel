import os
import gradio as gr
from ....utils import save_to_env


def create_model_tab(LOCALES):
    with gr.Blocks() as demo:
        with gr.Row():
            url = gr.Textbox(label=LOCALES["openai_url"],
                             value=os.getenv('OPENAI_BASE_URL'))
            url.change(save_to_env, [gr.State("OPENAI_BASE_URL"), url])
            api = gr.Textbox(label=LOCALES["openai_api"],
                             value=os.getenv('OPENAI_API_KEY'))
            api.change(save_to_env, [gr.State("OPENAI_API_KEY"), api])
        with gr.Row():
            chat_model = gr.Textbox(label=LOCALES["chat_model"],
                                    value=os.getenv('DEFAULT_CHAT_MODEL'),
                                    scale=3)
            chat_model.change(save_to_env, [gr.State("DEFAULT_CHAT_MODEL"), chat_model])
            embed_model = gr.Textbox(label=LOCALES["embedding_model"],
                                     value=os.getenv('DEFAULT_EMBED_MODEL'),
                                     scale=3)
            embed_model.change(save_to_env, [gr.State("DEFAULT_EMBED_MODEL"), embed_model])
    return demo
