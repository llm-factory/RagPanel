import gradio as gr


def create_splitter_tab(engine):
    with gr.Row():
        gr.Textbox(label="splitter path", info="path of your splitter(hugging_face or local), use tiktoken if empty")
        gr.Textbox(label="chunk size", info="the max size of each document chunk")
        gr.Textbox(label="chunk overlap", info="the size of overlap between document chunks")
        gr.Button("confirm")
        