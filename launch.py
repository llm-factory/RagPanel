from src import engine
import gradio as gr


def process_inputs(filepath, text_search, text_delete, text_replace, file_replace):
    if filepath is not None:
        return engine.process_file(filepath)
    if text_search != "":
        print(f"searching ", text_search)
        return engine.search(text_search, top_k=1)
    if text_delete != "":
        return engine.delete(text_delete, top_k=1)
    if text_replace != "" and file_replace is not None:
        return engine.replace(text_replace, file_replace)

if __name__ == '__main__': #demo
    iface = gr.Interface(
        fn=process_inputs,
        inputs=[
            gr.File(label="insert"),  # insert
            gr.Textbox(label="search"),  # search
            gr.Textbox(label="delete"),  # delete
            gr.Textbox(label="replace"), # replace query
            gr.File(label="replace") #replace file
        ],
        outputs=gr.Textbox(label="result")
    )
    iface.launch()
    