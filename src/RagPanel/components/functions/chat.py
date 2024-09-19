import gradio as gr

def create_chat_tab(chat_engine):
    with gr.Blocks() as demo:
        chat_bot = gr.Chatbot()
        query = gr.Textbox()
        chat_button = gr.Button("chat")
        chat_button.click(chat_engine.get_history, None, chat_bot).then(
            chat_engine.stream_chat, query
        )
    return demo
