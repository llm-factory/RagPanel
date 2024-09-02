import gradio as gr


def create_launch_rag_tab(engine):
    with gr.Blocks() as demo:
        gr.HTML("<b>launch a RAG demo, you should choose an action and upload your config file</b>")
        with gr.Row(equal_height=True):
            action = gr.Radio(["build", "launch", "dump"], label="parameter", info="action")
            config_file = gr.File(
                file_count="single",
                file_types=[".yml", "yaml"],
                label="config file",
                scale=3
            )

        launch_btn = gr.Button("launch")
    
    launch_btn.click(engine.launch_rag, [config_file, action], None)
    return demo
