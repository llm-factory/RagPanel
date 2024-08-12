import gradio as gr
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


from src import Engine, launch_rag


def info_file_upload():
    gr.Info("file uploaded")


def delete_docs(ids: list, docs: pd.DataFrame):
    for doc_id in ids:
        engine.delete_by_id(doc_id)

    docs = docs[~docs["id"].isin(ids)]
    if len(ids) == 1:
        gr.Info("1 file is deleted")
    elif len(ids) > 1:
        gr.Info(f"{len(ids)} files are deleted")
    return docs


def launch(config, action):
    if config and action:
        launch_rag(config, action)

        gr.Info("Success")


if __name__ == '__main__':
    # TODO:将目前的stdout内容同步到前端
    engine = Engine()
    with gr.Blocks() as demo:
        gr.HTML("<center><h1>RAG Panel</h1></center>")
        database_state = gr.State(value=[])
        search_result_state = gr.State()

        # TODO:增加新建数据库接口，可以输入名字新建数据库，调用engine.new_store实现
        # TODO:增加删除数据库接口，可以根据名字删除某个数据库，调用engine.rm_store实现
        gr.HTML("<b>create and choose your database</b>")
        with gr.Blocks():
            with gr.Tab("Create"):
                with gr.Row():
                    create_textbox = gr.Textbox(label="Create",
                                                info="create your database here",
                                                scale=3)
                    create_btn = gr.Button("Create")
            
            with gr.Tab("Delete"):
                with gr.Row():
                    delete_dropdown = gr.Dropdown(
                        choices=engine.store_names,
                        every=1,
                        label="Delete database",
                        allow_custom_value=True,
                        multiselect=True,
                        info="delete chosen database",
                        scale=3
                    )
                    delete_store_btn = gr.Button("Delete chosen database")
            
            with gr.Tab("Choose"):
                with gr.Row():
                    choose_dropdown = gr.Dropdown(
                        choices=engine.store_names,
                        every=1,
                        label="Select database",
                        allow_custom_value=True,
                        info="choose your database here",
                        scale=3
                    )
                    choose_btn = gr.Button("Choose this database")
                
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
                    delete_btn.click(delete_docs, [checkbox, search_result_state], search_result_state)

        def info_create_database():
            gr.Info(f"create successfully")
            
        def info_delete_database():
            gr.Info(f"delete successfully")

        def info_choose_database():
            gr.Info(f"change to {engine.cur_name}")
            
        create_btn.click(engine.create_database, [create_textbox, database_state], outputs=database_state).success(info_create_database, None, None)
            
        delete_store_btn.click(engine.remove_database, [delete_dropdown, database_state], outputs=database_state).success(info_delete_database, None, None)

        choose_btn.click(engine.change_to, choose_dropdown).success(info_choose_database, None, None)

        insert_btn.click(engine.insert, [file, proc_slider], progress_textbox, queue=True).success(info_file_upload, None, None)

        search_btn.click(engine.search, [search_box, slider], search_result_state)

        # replace_btn.click(engine.replace, [replace_content, file], None)
        
        launch_btn.click(launch, [config_file, action], None)

    demo.launch()
          