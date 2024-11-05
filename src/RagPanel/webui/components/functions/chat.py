import gradio as gr

def create_chat_tab(engine):
    with gr.Blocks() as demo:
        with gr.Column():
            with gr.Row():
                threshold_slider = gr.Slider(minimum=0, 
                                             maximum=2, 
                                             value=1, 
                                             step=0.02,
                                             label="threshold",
                                             info="results with Euclidean distance greater than the threshold will be filtered")
                top_k_slider = gr.Slider(minimum=1,
                                         maximum=32,
                                         value=5,
                                         step=1, 
                                         label="top_k",
                                         info="top k document chunks with the smallest Euclidean distance will be retrieved")
                template_box = gr.Textbox(value="充分理解以下事实描述：{context}\n\n回答下面的问题：{query}",
                                          scale=3,
                                          lines=3,
                                          label="template",
                                          info="RAG template")
                apply_btn = gr.Button("apply")
                apply_btn.click(engine.chat_engine.update, [top_k_slider, threshold_slider, template_box])
            def new_chat():
                return gr.Chatbot(label="chat", value="", placeholder="Ask me anything")
            chat_bot = new_chat()
            with gr.Row():
                def new_query():
                    return gr.Textbox(value="",
                                      scale=6,
                                      lines=5)
                query_box = new_query()
                with gr.Column():
                    chat_button = gr.Button("enter")
                    clear_button = gr.Button("clear history")
            chat_button.click(
                engine.chat_engine.ui_chat, 
                [chat_bot, query_box], 
                chat_bot
            )
            query_box.submit(
                engine.chat_engine.ui_chat, 
                [chat_bot, query_box], 
                chat_bot
            )
            query_box.submit(new_query, None, query_box)
            clear_button.click(engine.chat_engine.clear_history)
            clear_button.click(new_chat, None, chat_bot)
            clear_button.click(new_query, None, query_box)
    return demo
