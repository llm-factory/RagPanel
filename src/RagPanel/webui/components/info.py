import gradio as gr


def info_set_success():
    gr.Info('configuration applied successfully')

def info_create_database():
    gr.Info("create successfully")

def info_clear_database():
    gr.Info("clear successfully")
    
def info_destroy_database():
    gr.Info("destroy successfully")