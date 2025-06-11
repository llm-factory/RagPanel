import gradio as gr

def create_insert_tab(engine, LOCALES):
    with gr.Blocks() as insert_tab:
        # 标题区域
        gr.Markdown(
            f"## {LOCALES['insert_tab_title']}",
            elem_classes=["tab-title"]
        )
        
        # 可折叠的使用说明
        with gr.Accordion(
            label=LOCALES["usage_instructions"], 
            open=False,
            elem_classes=["instructions-accordion"]
        ):
            gr.Markdown(
                LOCALES["insert_instructions"],
                elem_classes=["instructions-content"]
            )
        
        # 主要操作区域
        with gr.Row():
            # 参数配置区域
            with gr.Column(scale=2):
                gr.Markdown(
                    f"### {LOCALES['processing_parameters']}",
                    elem_classes=["section-title"]
                )
                
                proc_slider = gr.Slider(
                    minimum=1,
                    maximum=32,
                    step=1,
                    value=16,
                    label=LOCALES["number_of_processes"],
                    info=LOCALES["processes_info"],
                    elem_classes=["parameter-slider"]
                )
                
                batch_slider = gr.Slider(
                    minimum=1,
                    maximum=4000,
                    step=1,
                    value=1000,
                    label=LOCALES["batch_embed"],
                    info=LOCALES["batch_embed_info"],
                    elem_classes=["parameter-slider"]
                )
            
            # 文件上传区域
            with gr.Column(scale=3):
                gr.Markdown(
                    f"### {LOCALES['file_upload_area']}",
                    elem_classes=["section-title"]
                )
                
                file = gr.File(
                    file_count="multiple",
                    label=LOCALES["select_files"],
                    file_types=None,
                    elem_classes=["file-upload"]
                )
                
                # 文件信息提示
                gr.Markdown(
                    LOCALES["file_upload_tips"],
                    elem_classes=["upload-tips"]
                )

        # 操作按钮区域
        with gr.Row():
            with gr.Column():
                insert_btn = gr.Button(
                    LOCALES["insert_file"],
                    variant="primary",
                    size="lg",
                    elem_classes=["insert-button"]
                )
        
        # 进度显示区域
        with gr.Row():
            with gr.Column():
                progress_textbox = gr.Textbox(
                    label=LOCALES["insertion_progress"],
                    interactive=False,
                    lines=3,
                    placeholder=LOCALES["progress_placeholder"],
                    elem_classes=["progress-display"]
                )
        
        # 状态信息区域
        with gr.Row():
            status_info = gr.Markdown(
                "",
                visible=False,
                elem_classes=["status-info"]
            )
        
    def info_file_upload():
        gr.Info(LOCALES["file_uploaded"])
        return gr.update(
            value=f"✅ {LOCALES['upload_complete_message']}",
            visible=True
        )
    
    def start_insertion():
        return gr.update(
            value=f"🔄 {LOCALES['insertion_started_message']}",
            visible=True
        )
    
    # 插入按钮点击事件
    insert_btn.click(
        start_insertion,
        outputs=status_info
    ).then(
        engine.insert, 
        inputs=[file, proc_slider, batch_slider],
        outputs=progress_textbox,
        queue=True
    ).success(
        info_file_upload,
        outputs=status_info
    )
    
    return insert_tab
