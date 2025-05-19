import gradio as gr
import pandas as pd

def create_chat_tab(engine, LOCALES):
    with gr.Blocks() as demo:
        with gr.Column():
            with gr.Row():
                template_box = gr.Textbox(value=LOCALES["template"],
                                          scale=3,
                                          lines=3,
                                          label=LOCALES["template_label"],
                                          info=LOCALES["template_info"])
                with gr.Column():
                    enable_rag_checkbox = gr.Checkbox(value=True,
                                                  label=LOCALES["enable_rag"])
                    show_docs_checkbox = gr.Checkbox(value=True,
                                                     label=LOCALES["show_docs"],
                                                     info=LOCALES["show_docs_info"])
                    save_history_checkbox = gr.Checkbox(value=True,
                                                        label=LOCALES["save_history"])
            def new_chat():
                return gr.Chatbot(label=LOCALES["chat"], value="", placeholder=LOCALES["hello"], type="messages")
            
            def assign(A):
                return A
            
            def update_chat(chat_bot, query):
                chat_bot += [{"role": "user", "content": query}]
                return chat_bot

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
                    
            query = gr.State()
            search_result_state = gr.State(pd.DataFrame())

            chat_button.click(
                assign, [query_box], [query]
            ).then(
                new_query, None, query_box
            ).then(
                update_chat, [chat_bot, query], chat_bot
            ).then(
                engine.chat_engine.update, 
                [template_box, enable_rag_checkbox, show_docs_checkbox, save_history_checkbox]
            ).then(
                engine.chat_engine.retrieve,
                [query],
                search_result_state
            ).then(
                engine.chat_engine.ui_chat, 
                [chat_bot, search_result_state], 
                chat_bot
            )
            
            query_box.submit(
                assign, [query_box], [query]
            ).then(
                new_query, None, query_box
            ).then(
                update_chat, [chat_bot, query], chat_bot
            ).then(
                engine.chat_engine.update, 
                [template_box, enable_rag_checkbox, show_docs_checkbox, save_history_checkbox]
            ).then(
                engine.chat_engine.retrieve,
                [query],
                search_result_state
            ).then(
                engine.chat_engine.ui_chat, 
                [chat_bot, search_result_state], 
                chat_bot
            )
            
            clear_button.click(
                engine.chat_engine.clear_history
            ).then(
                new_chat, None, chat_bot
            ).then(
                new_query, None, query_box
            ).then(
                lambda: pd.DataFrame(), None, search_result_state
            )

            @gr.render(inputs=search_result_state, triggers=[search_result_state.change])
            def show_search_results(docs: pd.DataFrame):
                if any(docs):
                    gr.Dataframe(docs[["content"]], label=LOCALES["retrieved_docs"])

    return demo
