import gradio as gr

def create_delete_tab(engine, LOCALES):
    def get_delete_dropdown():
        return gr.Dropdown(
            choices=[path.split('/')[-1] for path in engine.file_history],
            multiselect=True,
            type="index",
            allow_custom_value=True,
            label=LOCALES["delete_files"]
        )
    
    with gr.Blocks():
        dropdown = get_delete_dropdown()
        delete_button = gr.Button(LOCALES["delete_selected_files"])
        
    def info_file_deleted():
        gr.Info(LOCALES["files deleted"])

    gr.Timer().tick(get_delete_dropdown, outputs=dropdown)

    delete_button.click(engine.delete_by_file, dropdown).success(info_file_deleted)
