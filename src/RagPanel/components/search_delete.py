import gradio as gr
import pandas as pd

def create_search_delete_tab(engine, search_result_state):
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                threshold_slider = gr.Slider(0, 1, step=0.02, label="threshold", info="results with similarity less than the threshold will be filtered")
                top_k_slider = gr.Slider(1, 10, step=1, label="top_k", info="k document chunks with the highest similarity will be retrieved")
            search_box = gr.Textbox(label="Query", lines=10, scale=3)

        with gr.Row():
            search_btn = gr.Button("Search file")
            delete_btn = gr.Button("Delete")

        search_btn.click(engine.search, [search_box, threshold_slider, top_k_slider], search_result_state)

    @gr.render(inputs=search_result_state, triggers=[search_result_state.change])
    def show_search_results(docs: pd.DataFrame):
        if any(docs):
            with gr.Row():
                checkbox = gr.Checkboxgroup(choices=docs["id"].tolist(), label="select file to delete")
                gr.DataFrame(value=docs)
                delete_btn.click(engine.delete, [checkbox, search_result_state], search_result_state)
        else:
            gr.Warning("No matching docs")
    return demo
