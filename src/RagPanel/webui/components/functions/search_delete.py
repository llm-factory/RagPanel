import gradio as gr
import pandas as pd

def create_search_delete_tab(engine, search_result_state, LOCALES):
    with gr.Blocks() as demo:
        with gr.Row():
            search_box = gr.Textbox(label=LOCALES["query"],
                                    lines=5,
                                    scale=3)

        with gr.Row():
            search_btn = gr.Button(LOCALES["search_file"])
            delete_btn = gr.Button(LOCALES["delete_btn_1"])

        search_btn.click(engine.search,
                         [search_box],
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
