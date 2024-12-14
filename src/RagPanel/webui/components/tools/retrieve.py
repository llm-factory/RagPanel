import os
import gradio as gr
from ....utils import save_to_env


def create_retrieve_tab(engine, LOCALES):
    with gr.Blocks() as demo:
        with gr.Row():
            rag_dropdown = gr.Dropdown(label=LOCALES["RAG_Method"],
                                        choices=["naive", "graph"],
                                        value=os.getenv('RAG_METHOD', "naive"),
                                        type="value")
            rag_dropdown.change(save_to_env, [gr.State("RAG_METHOD"), rag_dropdown])
            
            def get_second_conf(rag):
                if rag == 'naive':
                    rerank_dropdown = gr.Textbox(label=LOCALES["reranker"],
                                        value="None")
                    return rerank_dropdown
                elif rag == 'graph':
                    cluster_slider = gr.Textbox(value=1,
                                        label=LOCALES["cluster_level"])
                    return cluster_slider
                
            second_conf = get_second_conf(os.getenv('RAG_METHOD', "naive"))
            second_conf.change(save_to_env, [rag_dropdown, second_conf])
            rag_dropdown.change(get_second_conf, rag_dropdown, second_conf)
                
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
        