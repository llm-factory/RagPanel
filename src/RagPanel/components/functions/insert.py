import gradio as gr


def create_insert_tab(engine):
    with gr.Blocks() as demo:
        with gr.Row():
            proc_slider = gr.Slider(minimum=1,
                                    maximum=32,
                                    step=1,
                                    label="multiprocess",
                                    info="set the number of processes",
                                    scale=1)
            file = gr.File(file_count="multiple",
                label="add file",
                scale=3)

        insert_btn = gr.Button("add file to database")
        progress_textbox = gr.Textbox(label="insertion progress",
                                        info="insertion progress is shown here")
        
    def info_file_upload():
        gr.Info("file uploaded")
    
    insert_btn.click(engine.insert, 
                     [file, proc_slider],
                     progress_textbox,
                     queue=True).success(info_file_upload)
    return demo
