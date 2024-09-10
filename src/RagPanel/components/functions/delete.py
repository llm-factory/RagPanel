import gradio as gr

def create_delete_tab(engine):
    def get_delete_dropdown():
        return gr.Dropdown(
            choices=engine.file_history,
            multiselect=True,
            allow_custom_value=True,
            label="delete files"
        )
    
    with gr.Blocks() as demo:
        dropdown = get_delete_dropdown()
        delete_button = gr.Button("delete selected files")
        
    def info_file_deleted():
        gr.Info("files deleted")

    gr.Timer().tick(get_delete_dropdown, outputs=dropdown)

    delete_button.click(engine.delete_by_file, dropdown).success(info_file_deleted)
