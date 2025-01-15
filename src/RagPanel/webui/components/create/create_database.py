import os
import gradio as gr


def create_database_block(engine, collection_name, LOCALES):
    def get_storage_path(storage):
        default_path = ""
        if storage is not None:
            if storage == 'redis':
                default_path = os.getenv("REDIS_URI")
            elif storage == 'es':
                default_path = os.getenv("ELASTICSEARCH_URI")
        else:
            default_path = os.getenv("REDIS_URI")
        storage_path = gr.Textbox(
            label=LOCALES["kv_storage_uri"],
            value=default_path,
            scale=2
        )
        return storage_path


    def get_graph_storage_path(graph_storage):
        label = LOCALES["graph_storage_uri"]
        if graph_storage is not None:
            if graph_storage == 'neo4j':
                default_path = os.getenv("NEO4J_URI")
            elif graph_storage == 'None':
                default_path = "None"
        else:
            default_path = os.getenv("NEO4J_URI")
        graph_storage_path = gr.Textbox(
            label=label,
            value=default_path,
            scale=2
        )
        return graph_storage_path
    
    
    def get_vectorstore_path(vectorstore):
        label = LOCALES["vectorstore_uri"]
        if vectorstore is not None:
            if vectorstore == 'chroma':
                default_path = os.getenv("CHROMA_PATH")
                label = LOCALES["vectorstore_path"]
            elif vectorstore == 'milvus':
                default_path = os.getenv("MILVUS_URI")
        else:
            default_path = os.getenv("CHROMA_PATH")
        vectorstore_path = gr.Textbox(
            label=label,
            value=default_path,
            scale=2
        )
        return vectorstore_path


    def get_vectorstore_token(vectorstore):
        visible = False
        if vectorstore == 'milvus':
            visible = True
        vectorstore_token = gr.Textbox(
            label=LOCALES["vectorstore_token"],
            info=LOCALES["token_info"],
            value="0",
            visible=visible
        )
        return vectorstore_token

    with gr.Blocks() as demo:
        with gr.Row():
            storage = os.getenv("STORAGE")
            storage_choice = gr.Dropdown(
                label=LOCALES["kv_storage"],
                choices=engine.supported_storages,
                value=storage,
                allow_custom_value=True
            )

            storage_path = get_storage_path(storage)
            storage_choice.change(get_storage_path, storage_choice, storage_path)

            collection = gr.Textbox(
                value=collection_name,
                label=LOCALES["collection_name"],
            )

        with gr.Row():
            vectorstore = os.getenv('VECTORSTORE')
            vectorstore_choice = gr.Dropdown(
                label=LOCALES["vectorstore"],
                choices=engine.supported_vectorstores,
                value=vectorstore,
                allow_custom_value=True
            )

            vectorstore_path = get_vectorstore_path(vectorstore)
            vectorstore_choice.change(get_vectorstore_path, vectorstore_choice, vectorstore_path)
            
            vectorstore_token = get_vectorstore_token(vectorstore)
            vectorstore_choice.change(get_vectorstore_token, vectorstore_choice, vectorstore_token)
            
        with gr.Row():
            graph_storage = os.getenv('GRAPH_STORAGE')
            graph_storage_choice = gr.Dropdown(
                label=LOCALES["graph_storage"],
                choices=engine.supported_graph_storages,
                value=graph_storage,
                info=LOCALES["graph_storage_info"],
                allow_custom_value=True
            )
            graph_storage_path = get_graph_storage_path(graph_storage)
            graph_storage_choice.change(get_graph_storage_path, graph_storage_choice, graph_storage_path)

        with gr.Row():
            database_confirm_btn = gr.Button(LOCALES["apply_and_save"])
            database_clear_btn = gr.Button(LOCALES["clear_database"])

    database_confirm_btn.click(engine.create_database,
                                [collection, storage_choice, storage_path, vectorstore_choice, vectorstore_path, vectorstore_token, graph_storage_choice, graph_storage_path]
                                ).success(gr.Info, gr.State(LOCALES["configuration_applied"]))
    database_clear_btn.click(engine.clear_database).success(gr.Info, gr.State(LOCALES["cleared_successfully"]))
    return demo
