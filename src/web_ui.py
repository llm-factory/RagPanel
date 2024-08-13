import gradio as gr
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


from .engine import Engine, launch_rag


def info_file_upload():
    gr.Info("file uploaded")


def delete_docs(engine: Engine, ids: list, docs: pd.DataFrame):
    for doc_id in ids:
        engine.delete_by_id(doc_id)

    docs = docs[~docs["id"].isin(ids)]
    if len(ids) == 1:
        gr.Info("1 file is deleted")
    elif len(ids) > 1:
        gr.Info(f"{len(ids)} files are deleted")
    return docs



def launch():
    engine = Engine()
    with gr.Blocks() as demo:
        gr.HTML("<center><h1>RAG Panel</h1></center>")
        search_result_state = gr.State()


        gr.HTML("<b>choose your database</b>")
        # TODO: 增加更多选择项(数据库类型、嵌入模型、分割器等)
        with gr.Blocks():
            with gr.Row():
                database_textbox = gr.Textbox(
                    label="Database name",
                    info="enter the name of your database",
                    scale=3
                )
                database_confirm_btn = gr.Button("Confirm")
            with gr.Row():
                database_clear_btn = gr.Button("Clear database")
                database_destroy_btn = gr.Button("Destroy database")
                
        gr.HTML("<b>insert, search and delete</b>")
        with gr.Tab("Insert"):
            with gr.Row():
                proc_slider = gr.Slider(1, 32, step=1, label="Multiprocess", info="set the number of processes", scale=1)
                file = gr.File(
                    file_count="multiple",
                    file_types=[".csv", ".txt"],
                    label="Add file",
                    scale=3
                )

            insert_btn = gr.Button("Add file to database")

            progress_textbox = gr.Textbox(label="Insertion progress",
                                          info="insertion progress is shown here")

        with gr.Tab("Search"):
            with gr.Row():
                slider = gr.Slider(1, 10, step=1, label="top_k")
                search_box = gr.Textbox(label="Query", lines=10, scale=3)

            with gr.Row():
                search_btn = gr.Button("Search file")
                delete_btn = gr.Button("Delete")

        # TODO:修改合适逻辑
        # with gr.Tab("Replace"):
        #     with gr.Row():
        #         replace_content = gr.Textbox(label="Content", lines=10)

        #         replace_file = gr.File(
        #             file_count="single",
        #             file_types=[".csv", ".txt"],
        #             label="Replace file"
        #         )

        #     replace_btn = gr.Button("Replace")

        with gr.Tab("Launch"):
            gr.HTML("<b>launch a RAG demo, you should choose an action and upload your config file</b>")
            with gr.Row(equal_height=True):
                action = gr.Radio(["build", "launch", "dump"], label="Parameter", info="action")
                config_file = gr.File(
                    file_count="single",
                    file_types=[".yml", "yaml"],
                    label="Config file",
                    scale=3
                )

            launch_btn = gr.Button("Launch")


        @gr.render(inputs=search_result_state, triggers=[search_result_state.change])
        def show_search_results(docs: pd.DataFrame):
            if any(docs):
                with gr.Row():
                    checkbox = gr.Checkboxgroup(choices=docs["id"].tolist(), label="select file to delete")
                    gr.DataFrame(value=docs)
                    delete_btn.click(delete_docs, [engine, checkbox, search_result_state], search_result_state)
            else:
                gr.Info("No matching docs")

        def info_create_database():
            gr.Info("create successfully")
        
        def info_clear_database():
            gr.Info("clear successfully")
            
        def info_destroy_database():
            gr.Info("destroy successfully")
            
        database_confirm_btn.click(engine.create_database, database_textbox).success(info_create_database)

        database_clear_btn.click(engine.clear_database).success(info_clear_database)

        database_destroy_btn.click(engine.destroy_database).success(info_destroy_database)

        insert_btn.click(engine.insert, [file, proc_slider], progress_textbox, queue=True).success(info_file_upload)

        search_btn.click(engine.search, [search_box, slider], search_result_state)

        # replace_btn.click(engine.replace, [replace_content, file], None)
        
        launch_btn.click(launch_rag, [config_file, action], None)

    demo.launch()
          