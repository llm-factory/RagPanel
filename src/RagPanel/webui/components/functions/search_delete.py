import gradio as gr
import pandas as pd

def create_search_delete_tab(engine, search_result_state, LOCALES):
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                threshold_slider = gr.Slider(minimum=0,
                                             maximum=2,
                                             value=1, 
                                             step=0.02,
                                             label=LOCALES["threshold"],
                                             info=LOCALES["threshold_info"])
                top_k_slider = gr.Slider(minimum=1, 
                                         maximum=32,
                                         value=5,
                                         step=1,
                                         label="top_k",
                                         info=LOCALES["top_k_info"])
                rerank_dropdown = gr.Dropdown(label="reranker",
                                              choices=["None", "Cohere"],
                                              value="None",
                                              type="value")
            search_box = gr.Textbox(label=LOCALES["query"],
                                    lines=10,
                                    scale=3)

        with gr.Row():
            search_btn = gr.Button(LOCALES["search_file"])
            delete_btn = gr.Button(LOCALES["delete_btn_1"])

        search_btn.click(engine.search,
                         [search_box, top_k_slider, rerank_dropdown, threshold_slider],
                         search_result_state)

    @gr.render(inputs=search_result_state, triggers=[search_result_state.change])
    def show_search_results(docs: pd.DataFrame):
        if any(docs):
            with gr.Row():
                checkbox = gr.Checkboxgroup(choices=docs["content"].tolist(),
                                            type="index", 
                                            label=LOCALES["select_file_delete"])
                delete_btn.click(engine.delete,
                                 [checkbox, search_result_state],
                                 search_result_state)
        else:
            gr.Warning(LOCALES["No_matching_docs"])
    return demo
