import os
import gradio as gr


def create_model_tab(engine):
    with gr.Blocks() as demo:
        with gr.Row():
            url = gr.Textbox(label="openai base url", info="base url of openai model or imitater", value=os.environ['OPENAI_BASE_URL'])
            api = gr.Textbox(label="openai api key", info="api key of openai model or imitater", value=os.environ['OPENAI_API_KEY'])
        with gr.Row():
            chat_model = gr.Textbox(label="chat model", info="chat model name", value=os.environ['DEFAULT_CHAT_MODEL'], scale=3)
            embed_model = gr.Textbox(label="embed model", info="embedding model name", value=os.environ['DEFAULT_EMBED_MODEL'], scale=3)
            confirm_button = gr.Button("confirm")
    confirm_button.click(engine.set_model, [url, api, chat_model, embed_model])
    return demo
