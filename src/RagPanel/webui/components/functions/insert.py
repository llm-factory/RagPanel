import gradio as gr


def create_insert_tab(engine, LOCALES):
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                proc_slider = gr.Slider(minimum=1,
                                    maximum=32,
                                    step=1,
                                    label=LOCALES["number_of_processes"])
                batch_slider = gr.Slider(minimum=1,
                                         maximum=4000,
                                         step=1,
                                         value=1000,
                                         label=LOCALES["batch_embed"],
                                         info=LOCALES["batch_embed_info"])
            file = gr.File(file_count="multiple",
                           scale=3)

        insert_btn = gr.Button(LOCALES["insert_file"])
        progress_textbox = gr.Textbox(label=LOCALES["insertion_progress"])
        
    def info_file_upload():
        gr.Info(LOCALES["file_uploaded"])
    
    insert_btn.click(engine.insert, 
                     [file, proc_slider, batch_slider],
                     progress_textbox,
                     queue=True).success(info_file_upload)
    return demo
