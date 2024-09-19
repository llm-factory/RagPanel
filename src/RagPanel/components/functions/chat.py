import gradio as gr

def create_chat_tab(chat_engine):
    with gr.Blocks() as demo:
        with gr.Column():
            with gr.Row():
                threshold_slider = gr.Slider(0, 2, value=1, step=0.02, label="threshold", info="results with Euclidean distance greater than the threshold will be filtered")
                top_k_slider = gr.Slider(1, 32, value=5, step=1, label="top_k", info="top k document chunks with the smallest Euclidean distance will be retrieved")
            history = chat_engine.get_history()
            chat_bot = gr.Chatbot(label="chat", value=history)
            with gr.Row():
                query_box = gr.Textbox(scale=6)
                chat_button = gr.Button("enter")
            chat_button.click(chat_engine.get_history, None, chat_bot).then(
                chat_engine.stream_chat, [chat_bot, query_box, threshold_slider, top_k_slider], chat_bot
            )
            query_box.submit(chat_engine.get_history, None, chat_bot).then(
                chat_engine.stream_chat, [chat_bot, query_box, threshold_slider, top_k_slider], chat_bot
            )
    return demo
