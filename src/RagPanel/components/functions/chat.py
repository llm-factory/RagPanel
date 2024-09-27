import gradio as gr

def create_chat_tab(chat_engine):
    with gr.Blocks() as demo:
        with gr.Column():
            with gr.Row():
                threshold_slider = gr.Slider(0, 2, value=1, step=0.02, label="threshold", info="results with Euclidean distance greater than the threshold will be filtered")
                top_k_slider = gr.Slider(1, 32, value=5, step=1, label="top_k", info="top k document chunks with the smallest Euclidean distance will be retrieved")
                template_box = gr.Textbox(value="充分理解以下事实描述：{context}\n\n回答下面的问题：{query}",
                                          scale=3,
                                          lines=3,
                                          label="template",
                                          info="RAG template")
            history = chat_engine.get_history()
            def new_chat():
                return gr.Chatbot(label="chat", value=history)
            chat_bot = new_chat()
            with gr.Row():
                query_box = gr.Textbox(scale=6,
                                       lines=5)
                with gr.Column():
                    chat_button = gr.Button("enter")
                    clear_button = gr.Button("clear history")
            chat_button.click(chat_engine.get_history, None, chat_bot).then(
                chat_engine.stream_chat, [chat_bot, query_box, threshold_slider, top_k_slider, template_box], chat_bot
            )
            query_box.submit(chat_engine.get_history, None, chat_bot).then(
                chat_engine.stream_chat, [chat_bot, query_box, threshold_slider, top_k_slider, template_box], chat_bot
            )
            clear_button.click(chat_engine.clear_history)
            clear_button.click(new_chat, None, chat_bot)
    return demo
