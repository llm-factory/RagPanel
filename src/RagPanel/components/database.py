import gradio as gr


def create_database_block(engine):
    with gr.Blocks() as demo:
        with gr.Row():
            database_textbox = gr.Textbox(
                label="Database name",
                info="enter the name of your database",
                scale=3
            )
            database_confirm_btn = gr.Button("Confirm")
        with gr.Row():
            database_clear_btn = gr.Button("Clear database")
            database_destroy_btn = gr.Button("Destroy database")

    def info_create_database():
        gr.Info("create successfully")
    
    def info_clear_database():
        gr.Info("clear successfully")
        
    def info_destroy_database():
        gr.Info("destroy successfully")

    database_confirm_btn.click(engine.create_database, database_textbox).success(info_create_database)
    database_clear_btn.click(engine.clear_database).success(info_clear_database)
    database_destroy_btn.click(engine.destroy_database).success(info_destroy_database)
    return demo
