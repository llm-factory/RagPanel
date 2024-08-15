import gradio as gr


def create_insert_tab(engine):
    with gr.Blocks() as demo:
        with gr.Row():
            proc_slider = gr.Slider(1, 32, step=1, label="Multiprocess", info="set the number of processes", scale=1)
            file = gr.File(
                file_count="multiple",
                file_types=[".csv", ".txt"],
                label="Add file",
                scale=3
            )

        insert_btn = gr.Button("Add file to database")
        progress_textbox = gr.Textbox(label="Insertion progress",
                                        info="insertion progress is shown here")
        
    def info_file_upload():
        gr.Info("file uploaded")
    
    insert_btn.click(engine.insert, [file, proc_slider], progress_textbox, queue=True).success(info_file_upload)
    return demo
