import gradio as gr

def create_delete_tab(engine, LOCALES):
    def get_delete_dropdown():
        return gr.Dropdown(
            choices=[path.split('/')[-1] for path in engine.file_history],
            multiselect=True,
            type="index",
            allow_custom_value=True,
            label=LOCALES["delete_files"],
            info=LOCALES["delete_files_info"]
        )
    
    with gr.Blocks() as delete_tab:
        # 标题区域
        gr.Markdown(
            f"## {LOCALES['delete_tab_title']}",
            elem_classes=["tab-title"]
        )
        
        # 可折叠的使用说明
        with gr.Accordion(
            label=LOCALES["usage_instructions"], 
            open=False,
            elem_classes=["instructions-accordion"]
        ):
            gr.Markdown(
                LOCALES["delete_instructions"],
                elem_classes=["instructions-content"]
            )
        
        # 主要操作区域
        with gr.Row():
            with gr.Column(scale=4):
                dropdown = get_delete_dropdown()
            
        with gr.Row():
            with gr.Column(scale=1):
                delete_button = gr.Button(
                    LOCALES["delete_selected_files"],
                    variant="stop",  # 使用红色警告样式
                    size="lg",
                    elem_classes=["delete-button"]
                )
        
        # 状态显示区域
        with gr.Row():
            status_text = gr.Textbox(
                label=LOCALES["operation_status"],
                interactive=False,
                visible=False,
                elem_classes=["status-display"]
            )
    
    def info_file_deleted():
        gr.Info(LOCALES["files_deleted"])
        return gr.update(
            value=LOCALES["delete_success_message"],
            visible=True
        )

    def handle_delete_error():
        gr.Warning(LOCALES["delete_error_message"])
        return gr.update(
            value=LOCALES["delete_failed_message"],
            visible=True
        )

    # 定时更新下拉菜单
    gr.Timer(value=0.5).tick(get_delete_dropdown, outputs=dropdown)

    # 删除按钮点击事件
    delete_button.click(
        engine.delete_by_file, 
        inputs=dropdown,
        outputs=status_text
    ).success(
        info_file_deleted,
        outputs=status_text
    )
    
    return delete_tab
