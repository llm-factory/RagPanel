import gradio as gr

def create_chat_tab(engine, LOCALES):
    with gr.Blocks() as demo:
        with gr.Column():
            with gr.Row():
                threshold_slider = gr.Slider(minimum=0, 
                                             maximum=2, 
                                             value=1, 
                                             step=0.02,
                                             label=LOCALES["threshold"],
                                             info=LOCALES["threshold_info"])
                top_k_slider = gr.Slider(minimum=1,
                                         maximum=32,
                                         value=5,
                                         step=1, 
                                         label="top_k",
                                         info=LOCALES["top_k_info"])
                template_box = gr.Textbox(value=LOCALES["template"],
                                          scale=3,
                                          lines=3,
                                          label=LOCALES["template_label"],
                                          info=LOCALES["template_info"])
            def new_chat():
                return gr.Chatbot(label=LOCALES["chat"], value="", placeholder=LOCALES["hello"])
            chat_bot = new_chat()
            with gr.Row():
                def new_query():
                    return gr.Textbox(value="",
                                      label="",
                                      scale=6,
                                      lines=5)
                query_box = new_query()
                with gr.Column():
                    chat_button = gr.Button(LOCALES["enter"], scale=3)
                    clear_button = gr.Button(LOCALES["clear_history"], scale=3)
                    
            chat_button.click(
                engine.chat_engine.update, 
                [top_k_slider, threshold_slider, 
                template_box]
            ).then(
                engine.chat_engine.ui_chat, 
                [chat_bot, query_box], 
                chat_bot
            )
            
            query_box.submit(
                engine.chat_engine.update, 
                [top_k_slider, threshold_slider, template_box]
            ).then(
                engine.chat_engine.ui_chat, 
                [chat_bot, query_box], 
                chat_bot
            ).then(new_query, None, query_box)
            
            clear_button.click(engine.chat_engine.clear_history)
            clear_button.click(new_chat, None, chat_bot)
            clear_button.click(new_query, None, query_box)
    return demo
