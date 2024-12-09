import os
import gradio as gr
from ....utils import save_to_env


def create_retriever_tab(engine, LOCALES):
    with gr.Blocks() as demo:
        with gr.Row():
            retriever_dropdown = gr.Dropdown(label=LOCALES["retriever"],
                                        choices=[LOCALES["dense"], LOCALES["sparse"], LOCALES["hybrid"]],
                                        value=LOCALES[os.getenv('RETRIEVER', "dense")],
                                        type="value")
            retriever_dropdown.change(save_to_env, [gr.State("RETRIEVER"), retriever_dropdown])
            rerank_dropdown = gr.Dropdown(label=LOCALES["reranker"],
                                        choices=["None", "Cohere"],
                                        value="None",
                                        type="value")
            rerank_dropdown.change(save_to_env, [gr.State("RERANKER"), rerank_dropdown])
            threshold_slider = gr.Slider(minimum=0,
                                        maximum=2,
                                        value=1, 
                                        step=0.02,
                                        label=LOCALES["threshold"],
                                        info=LOCALES["threshold_info"])
            threshold_slider.change(engine.set, [gr.State("tmp_threshold"), threshold_slider])
            top_k_slider = gr.Slider(minimum=1, 
                                    maximum=32,
                                    value=5,
                                    step=1,
                                    label="top_k",
                                    info=LOCALES["top_k_info"])
            top_k_slider.change(engine.set, [gr.State("tmp_top_k"), top_k_slider])
    return demo
        