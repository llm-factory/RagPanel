import gradio as gr
from dotenv import load_dotenv


load_dotenv() #must before following import


from src.engine import insert, delete, search, replace, launch_rag


def process_inputs(filepath, text_search, text_delete, text_replace, file_replace):
    if filepath is not None:
        return insert(filepath)
    if text_search != "":
        print(f"searching ", text_search)
        return search(text_search, top_k=1)
    if text_delete != "":
        return delete(text_delete, top_k=1)
    if text_replace != "" and file_replace is not None:
        return replace(text_replace, file_replace)
    else:
        launch_rag("config.yaml", "build")

if __name__ == '__main__': #demo
    iface = gr.Interface(
        fn=process_inputs,
        inputs=[
            gr.File(label="insert", file_count="multiple"),  # insert
            gr.Textbox(label="search"),  # search
            gr.Textbox(label="delete"),  # delete
            gr.Textbox(label="replace"), # replace query
            gr.File(label="replace") #replace file
        ],
        outputs=gr.Textbox(label="result")
    )
    iface.launch()
    