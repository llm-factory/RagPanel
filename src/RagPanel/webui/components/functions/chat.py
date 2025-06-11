import gradio as gr
import pandas as pd
from cardinal import ChatCollector  # 导入我们的收集器

def create_chat_tab(engine, LOCALES):
    # 创建聊天收集器（使用用户标识，可以根据实际情况调整）
    chat_collector = ChatCollector("main_user")
    
    with gr.Blocks(title="AI问答系统", theme=gr.themes.Soft()) as demo:
        with gr.Row():
            # 左侧：聊天管理（缩小比例）
            with gr.Column(scale=1, min_width=280):
                gr.Markdown("### 📋 聊天管理")
                
                # 会话选择
                def get_session_choices():
                    sessions = chat_collector.list_sessions()
                    choices = []
                    for session in sessions:
                        title = session["title"]
                        if session.get("is_active", False):
                            title = f"🟢 {title}"  # 活跃会话标记
                        choices.append(title)  # 只返回标题作为选项
                    return choices
                
                def get_current_session_title():
                    """获取当前会话标题作为默认值"""
                    current_session = chat_collector.get_current_session()
                    if current_session:
                        title = current_session.title
                        if current_session.is_active:
                            title = f"🟢 {title}"
                        return title
                    return "New Chat"
                
                session_dropdown = gr.Dropdown(
                    choices=get_session_choices(),
                    label="选择聊天记录",
                    value=get_current_session_title(),
                    interactive=True,
                    allow_custom_value=False  # 不允许自定义值
                )
                
                # 操作按钮
                with gr.Row():
                    new_chat_btn = gr.Button("🆕 新建聊天", variant="primary", size="sm")
                    load_chat_btn = gr.Button("📂 加载聊天", variant="secondary", size="sm")
                
                with gr.Row():
                    delete_chat_btn = gr.Button("🗑️ 删除聊天", variant="stop", size="sm")
                    refresh_btn = gr.Button("🔄 刷新列表", size="sm")
                
                # 系统配置按钮
                config_btn = gr.Button("⚙️ 系统配置", variant="secondary", size="sm")
                
                # 状态信息
                def get_initial_status():
                    stats = chat_collector.get_session_statistics()
                    current_session = chat_collector.get_current_session()
                    if current_session:
                        return f"当前会话: {current_session.title}\n共有 {stats['total_sessions']} 个会话"
                    return "系统就绪"
                
                status_msg = gr.Textbox(
                    label="状态信息",
                    value=get_initial_status(),
                    interactive=False,
                    lines=2
                )
                
                # 配置面板（显示在状态信息下方）
                with gr.Column(visible=False) as config_panel:
                    gr.Markdown("#### ⚙️ 配置选项")
                    
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
                        save_config_btn = gr.Button("💾 保存", variant="primary", size="sm")
                        cancel_config_btn = gr.Button("❌ 取消", variant="secondary", size="sm")
            
            # 右侧：聊天界面（增大比例）
            with gr.Column(scale=3):
                gr.Markdown("### 💬 聊天对话")
                
                # 聊天界面
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
                    """获取初始聊天内容"""
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
                
                # 输入框和发送按钮
                with gr.Row():
                    def new_query():
                        return gr.Textbox(
                            value="",
                            placeholder="请输入您的问题...",
                            label="",
                            scale=5,
                            lines=2,
                            show_label=False
                        )
                    query_box = new_query()
                    with gr.Column(scale=1):
                        chat_button = gr.Button(LOCALES["enter"], variant="primary", size="lg")
        
        # 文档检索结果显示区域
        search_result_state = gr.State(pd.DataFrame())
        
        # 状态变量
        query = gr.State()
        config_visible = gr.State(False)
        
        # 辅助函数
        def assign(A):
            return A
        
        def update_chat(chat_bot, query):
            chat_bot += [{"role": "user", "content": query}]
            return chat_bot
        
        def save_session_after_response(chat_bot):
            """在收到回复后保存会话并更新标题"""
            if chat_bot:
                success = chat_collector.save_current_conversation(chat_bot)
                if success:
                    # 如果是新会话且有消息，自动生成标题
                    current_session = chat_collector.get_current_session()
                    if current_session and len(current_session.messages) == 1:
                        # 使用第一个用户消息作为标题的一部分
                        first_message = chat_bot[0]["content"] if chat_bot else ""
                        auto_title = chat_collector.generate_session_title(first_message)
                        chat_collector.update_session_title(current_session.session_id, auto_title)
                if not success:
                    print("Failed to save conversation")
            return chat_bot
        
        # 根据标题查找会话ID的辅助函数
        def find_session_id_by_title(title):
            """根据标题查找会话ID"""
            if not title:
                return None
            
            # 移除活跃标记
            clean_title = title.replace("🟢 ", "")
            
            sessions = chat_collector.list_sessions()
            for session in sessions:
                if session["title"] == clean_title:
                    return session["session_id"]
            return None
        
        # 会话管理功能
        def create_new_session():
            session_id = chat_collector.create_session("New Chat")  # 默认标题
            session_choices = get_session_choices()
            current_title = get_current_session_title()
            current_session = chat_collector.get_current_session()
            status = f"新聊天会话已创建！\n当前会话: {current_session.title if current_session else '未知'}"
            return (
                gr.update(choices=session_choices, value=current_title),
                status,
                []  # 清空聊天界面
            )
        
        def load_selected_session(session_title):
            if not session_title:
                return gr.update(), "请选择要加载的聊天记录", gr.update()
            
            session_id = find_session_id_by_title(session_title)
            if not session_id:
                return gr.update(), "找不到对应的聊天记录", gr.update()
            
            success = chat_collector.set_current_session(session_id)
            if success:
                messages = chat_collector.get_session_messages(session_id)
                session = chat_collector.get_session(session_id)
                title = session.title if session else "未知会话"
                status = f"已加载聊天记录: {title}\n消息数量: {len(messages)//2}"
                
                # 更新下拉选择框的选项和值
                session_choices = get_session_choices()
                current_title = get_current_session_title()
                
                return (
                    gr.update(choices=session_choices, value=current_title),
                    status,
                    messages
                )
            else:
                return gr.update(), "加载聊天记录失败", gr.update()
        
        def delete_selected_session(session_title):
            if not session_title:
                return gr.update(), "请选择要删除的聊天记录", gr.update()
            
            session_id = find_session_id_by_title(session_title)
            if not session_id:
                return gr.update(), "找不到对应的聊天记录", gr.update()
            
            # 获取会话标题
            session = chat_collector.get_session(session_id)
            title = session.title if session else "未知会话"
            
            success = chat_collector.delete_session(session_id)
            session_choices = get_session_choices()
            current_title = get_current_session_title()
            
            if success:
                status = f"已删除聊天记录: {title}"
                current_session = chat_collector.get_current_session()
                if current_session:
                    status += f"\n当前会话: {current_session.title}"
                return (
                    gr.update(choices=session_choices, value=current_title),
                    status
                )
            else:
                return (
                    gr.update(choices=session_choices),
                    f"删除聊天记录失败: {title}"
                )
        
        def refresh_session_list():
            session_choices = get_session_choices()
            current_title = get_current_session_title()
            stats = chat_collector.get_session_statistics()
            status = f"列表已刷新\n共有 {stats['total_sessions']} 个会话"
            return gr.update(choices=session_choices, value=current_title), status
        
        # 配置面板切换
        def toggle_config_panel(visible):
            return gr.update(visible=not visible), not visible
        
        def save_config():
            return gr.update(visible=False), False, "配置已保存！"
        
        def cancel_config():
            return gr.update(visible=False), False, "已取消配置修改"
        
        # 绑定会话管理事件
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
        
        # 配置面板事件
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
        
        # 聊天功能事件绑定
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
            # 更新下拉选择框
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
            # 更新下拉选择框
            refresh_session_list,
            outputs=[session_dropdown, status_msg]
        )
        
        # 文档检索结果显示
        @gr.render(inputs=search_result_state, triggers=[search_result_state.change])
        def show_search_results(docs: pd.DataFrame):
            if any(docs):
                with gr.Accordion("📄 检索到的相关文档", open=True):
                    gr.Dataframe(
                        docs[["content"]], 
                        label=LOCALES["retrieved_docs"],
                        wrap=True,
                        show_label=False
                    )
        
        # 使用说明（折叠状态）
        with gr.Accordion("📖 使用说明", open=False):
            gr.Markdown("""
            ### 🌟 功能说明：
            
            #### 聊天管理：
            - **🆕 新建聊天**：创建一个新的聊天会话
            - **📂 加载聊天**：从下拉列表中选择并加载历史聊天记录
            - **🗑️ 删除聊天**：删除选中的聊天记录（不可恢复）
            - **🔄 刷新列表**：更新聊天记录列表
            
            #### 系统配置：
            - **⚙️ 系统配置**：设置模板、RAG开关、文档显示等选项
            - **💾 保存**：保存当前配置设置
            - **❌ 取消**：取消配置修改
            
            #### 智能问答：
            - 支持RAG文档检索增强回答
            - 自动保存聊天历史到Redis数据库
            - 显示检索到的相关文档
            - 自动根据对话内容生成聊天标题
            
            ### 🚀 使用步骤：
            1. 点击"新建聊天"开始新对话
            2. 在消息输入框中输入问题，点击"发送"或按Enter键
            3. 系统会自动检索相关文档并生成回答
            4. 可以随时切换或管理不同的聊天会话
            5. 通过"系统配置"调整系统参数
            
            ### 💾 数据存储：
            - 聊天记录存储在Redis数据库中
            - 支持持久化和高性能访问
            - 自动备份和恢复功能
            - 自动生成有意义的聊天标题
            """)

    return demo
