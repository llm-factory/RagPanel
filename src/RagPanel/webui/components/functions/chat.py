import gradio as gr
import pandas as pd
from cardinal import ChatCollector

def create_chat_tab(engine, LOCALES):
    chat_collector = ChatCollector("main_user")
    
    with gr.Blocks(title=LOCALES["ai_qa_system"], theme=gr.themes.Soft()) as demo:
        with gr.Row():
            with gr.Column(scale=1, min_width=280):
                gr.Markdown(f"### 📋 {LOCALES['chat_management']}")
                
                def get_session_choices():
                    sessions = chat_collector.list_sessions()
                    choices = []
                    for session in sessions:
                        title = session["title"]
                        if session.get("is_active", False):
                            title = f"🟢 {title}"
                        choices.append(title)
                    return choices
                
                def get_current_session_title():
                    current_session = chat_collector.get_current_session()
                    if current_session:
                        title = current_session.title
                        if current_session.is_active:
                            title = f"🟢 {title}"
                        return title
                    return LOCALES["new_chat"]
                
                session_dropdown = gr.Dropdown(
                    choices=get_session_choices(),
                    label=LOCALES["select_chat_history"],
                    value=get_current_session_title(),
                    interactive=True,
                    allow_custom_value=False
                )
                
                with gr.Row():
                    new_chat_btn = gr.Button(f"🆕 {LOCALES['new_chat']}", variant="primary", size="sm")
                    load_chat_btn = gr.Button(f"📂 {LOCALES['load_chat']}", variant="secondary", size="sm")
                
                with gr.Row():
                    delete_chat_btn = gr.Button(f"🗑️ {LOCALES['delete_chat']}", variant="stop", size="sm")
                    refresh_btn = gr.Button(f"🔄 {LOCALES['refresh_list']}", size="sm")
                
                config_btn = gr.Button(f"⚙️ {LOCALES['system_config']}", variant="secondary", size="sm")
                
                def get_initial_status():
                    stats = chat_collector.get_session_statistics()
                    current_session = chat_collector.get_current_session()
                    if current_session:
                        return f"{LOCALES['current_session']}: {current_session.title}\n{LOCALES['total_sessions']}: {stats['total_sessions']}"
                    return LOCALES["system_ready"]
                
                status_msg = gr.Textbox(
                    label=LOCALES["status_info"],
                    value=get_initial_status(),
                    interactive=False,
                    lines=2
                )
                
                with gr.Column(visible=False) as config_panel:
                    gr.Markdown(f"#### ⚙️ {LOCALES['config_options']}")
                    
                    template_box = gr.Textbox(
                        value=LOCALES["template"],
                        lines=3,
                        label=LOCALES["template_label"],
                        info=LOCALES["template_info"],
                        scale=1
                    )
                    
                    enable_rag_checkbox = gr.Checkbox(
                        value=True,
                        label=LOCALES["enable_rag"]
                    )
                    show_docs_checkbox = gr.Checkbox(
                        value=True,
                        label=LOCALES["show_docs"],
                        info=LOCALES["show_docs_info"]
                    )
                    save_history_checkbox = gr.Checkbox(
                        value=True,
                        label=LOCALES["save_history"]
                    )
                    
                    with gr.Row():
                        save_config_btn = gr.Button(f"💾 {LOCALES['save']}", variant="primary", size="sm")
                        cancel_config_btn = gr.Button(f"❌ {LOCALES['cancel']}", variant="secondary", size="sm")
            
            with gr.Column(scale=3):
                gr.Markdown(f"### 💬 {LOCALES['chat_dialogue']}")
                
                def new_chat():
                    return gr.Chatbot(
                        label=LOCALES["chat"], 
                        value=[], 
                        placeholder=LOCALES["hello"], 
                        type="messages",
                        height=600,
                        show_label=False,
                        bubble_full_width=False,
                        show_copy_button=True
                    )
                
                def get_initial_chat():
                    current_session_id = chat_collector.get_current_session_id()
                    if current_session_id:
                        messages = chat_collector.get_session_messages(current_session_id)
                        return gr.Chatbot(
                            label=LOCALES["chat"], 
                            value=messages, 
                            placeholder=LOCALES["hello"], 
                            type="messages",
                            height=600,
                            show_label=False,
                            bubble_full_width=False,
                            show_copy_button=True
                        )
                    return new_chat()
                
                chat_bot = get_initial_chat()
                
                with gr.Row():
                    def new_query():
                        return gr.Textbox(
                            value="",
                            placeholder=LOCALES["input_placeholder"],
                            label="",
                            scale=5,
                            lines=2,
                            show_label=False
                        )
                    query_box = new_query()
                    with gr.Column(scale=1):
                        chat_button = gr.Button(LOCALES["send"], variant="primary", size="lg")

        
        search_result_state = gr.State(pd.DataFrame())
        
        query = gr.State()
        config_visible = gr.State(False)
        
        def assign(A):
            return A
        
        def update_chat(chat_bot, query):
            chat_bot += [{"role": "user", "content": query}]
            return chat_bot
        
        def save_session_after_response(chat_bot):
            if chat_bot:
                success = chat_collector.save_current_conversation(chat_bot)
                if success:
                    current_session = chat_collector.get_current_session()
                    if current_session and len(current_session.messages) == 1:
                        first_message = chat_bot[0]["content"] if chat_bot else ""
                        auto_title = chat_collector.generate_session_title(first_message)
                        chat_collector.update_session_title(current_session.session_id, auto_title)
                if not success:
                    print("Failed to save conversation")
            return chat_bot
        
        def find_session_id_by_title(title):
            if not title:
                return None
            
            clean_title = title.replace("🟢 ", "")
            
            sessions = chat_collector.list_sessions()
            for session in sessions:
                if session["title"] == clean_title:
                    return session["session_id"]
            return None
        
        def create_new_session():
            session_id = chat_collector.create_session(LOCALES["new_chat"])
            session_choices = get_session_choices()
            current_title = get_current_session_title()
            current_session = chat_collector.get_current_session()
            status = f"{LOCALES['new_chat_created']}\n{LOCALES['current_session']}: {current_session.title if current_session else LOCALES['unknown']}"
            return (
                gr.update(choices=session_choices, value=current_title),
                status,
                []
            )
        
        def load_selected_session(session_title):
            if not session_title:
                return gr.update(), LOCALES["select_chat_to_load"], gr.update()
            
            session_id = find_session_id_by_title(session_title)
            if not session_id:
                return gr.update(), LOCALES["chat_not_found"], gr.update()
            
            success = chat_collector.set_current_session(session_id)
            if success:
                messages = chat_collector.get_session_messages(session_id)
                session = chat_collector.get_session(session_id)
                title = session.title if session else LOCALES["unknown_session"]
                status = f"{LOCALES['chat_loaded']}: {title}\n{LOCALES['message_count']}: {len(messages)//2}"
                
                session_choices = get_session_choices()
                current_title = get_current_session_title()
                
                return (
                    gr.update(choices=session_choices, value=current_title),
                    status,
                    messages
                )
            else:
                return gr.update(), LOCALES["load_chat_failed"], gr.update()
        
        def delete_selected_session(session_title):
            if not session_title:
                return gr.update(), LOCALES["select_chat_to_delete"], gr.update()
            
            session_id = find_session_id_by_title(session_title)
            if not session_id:
                return gr.update(), LOCALES["chat_not_found"], gr.update()
            
            session = chat_collector.get_session(session_id)
            title = session.title if session else LOCALES["unknown_session"]
            
            success = chat_collector.delete_session(session_id)
            session_choices = get_session_choices()
            current_title = get_current_session_title()
            
            if success:
                status = f"{LOCALES['chat_deleted']}: {title}"
                current_session = chat_collector.get_current_session()
                if current_session:
                    status += f"\n{LOCALES['current_session']}: {current_session.title}"
                return (
                    gr.update(choices=session_choices, value=current_title),
                    status
                )
            else:
                return (
                    gr.update(choices=session_choices),
                    f"{LOCALES['delete_chat_failed']}: {title}"
                )
        
        def refresh_session_list():
            session_choices = get_session_choices()
            current_title = get_current_session_title()
            stats = chat_collector.get_session_statistics()
            status = f"{LOCALES['list_refreshed']}\n{LOCALES['total_sessions']}: {stats['total_sessions']}"
            return gr.update(choices=session_choices, value=current_title), status
        
        def toggle_config_panel(visible):
            return gr.update(visible=not visible), not visible
        
        def save_config():
            return gr.update(visible=False), False, LOCALES["config_saved"]
        
        def cancel_config():
            return gr.update(visible=False), False, LOCALES["config_cancelled"]
        
        new_chat_btn.click(
            create_new_session,
            outputs=[session_dropdown, status_msg, chat_bot]
        )
        
        load_chat_btn.click(
            load_selected_session,
            inputs=[session_dropdown],
            outputs=[session_dropdown, status_msg, chat_bot]
        )
        
        delete_chat_btn.click(
            delete_selected_session,
            inputs=[session_dropdown],
            outputs=[session_dropdown, status_msg]
        )
        
        refresh_btn.click(
            refresh_session_list,
            outputs=[session_dropdown, status_msg]
        )
        
        config_btn.click(
            toggle_config_panel,
            inputs=[config_visible],
            outputs=[config_panel, config_visible]
        )
        
        save_config_btn.click(
            save_config,
            outputs=[config_panel, config_visible, status_msg]
        )
        
        cancel_config_btn.click(
            cancel_config,
            outputs=[config_panel, config_visible, status_msg]
        )
        
        chat_button.click(
            assign, [query_box], [query]
        ).then(
            new_query, None, query_box
        ).then(
            update_chat, [chat_bot, query], chat_bot
        ).then(
            engine.chat_engine.update, 
            [template_box, show_docs_checkbox, save_history_checkbox]
        ).then(
            engine.chat_engine.retrieve,
            [query, enable_rag_checkbox],
            search_result_state
        ).then(
            engine.chat_engine.ui_chat, 
            [chat_bot, search_result_state], 
            chat_bot
        ).then(
            save_session_after_response,
            [chat_bot],
            [chat_bot]
        ).then(
            refresh_session_list,
            outputs=[session_dropdown, status_msg]
        )
        
        query_box.submit(
            assign, [query_box], [query]
        ).then(
            new_query, None, query_box
        ).then(
            update_chat, [chat_bot, query], chat_bot
        ).then(
            engine.chat_engine.update, 
            [template_box, show_docs_checkbox, save_history_checkbox]
        ).then(
            engine.chat_engine.retrieve,
            [query, enable_rag_checkbox],
            search_result_state
        ).then(
            engine.chat_engine.ui_chat, 
            [chat_bot, search_result_state], 
            chat_bot
        ).then(
            save_session_after_response,
            [chat_bot],
            [chat_bot]
        ).then(
            refresh_session_list,
            outputs=[session_dropdown, status_msg]
        )
        
        @gr.render(inputs=search_result_state, triggers=[search_result_state.change])
        def show_search_results(docs: pd.DataFrame):
            if any(docs):
                with gr.Accordion(f"📄 {LOCALES['retrieved_related_docs']}", open=True):
                    gr.Dataframe(
                        docs[["content"]], 
                        label=LOCALES["retrieved_docs"],
                        wrap=True,
                        show_label=False
                    )
        
        with gr.Accordion(f"📖 {LOCALES['usage_instructions']}", open=False):
            gr.Markdown(LOCALES["usage_instructions_content"])

    return demo
