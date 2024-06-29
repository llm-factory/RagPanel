from src import engine
import gradio as gr


def process_inputs(filepath, text_search, text_delete, text_replace, file_replace):
    if filepath is not None:
        return engine.process_file(filepath)
    if text_search is not None:
        return engine.search(text_search)
    if text_delete is not None:
        return engine.delete(text_delete)
    if text_replace is not None and file_replace is not None:
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
    