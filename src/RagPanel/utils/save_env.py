import os


envs_to_save = [
    "OPENAI_BASE_URL",
    "OPENAI_API_KEY",
    "DEFAULT_EMBED_MODEL",
    "DEFAULT_CHAT_MODEL",
    "HF_TOKENIZER_PATH",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_CHUNK_OVERLAP",
    "STORAGE",
    "RETRIEVER",
    "RERANKER",
    "SEARCH_TARGET",
    "REDIS_URI",
    "ELASTICSEARCH_URI",
    "GRAPH_STORAGE",
    "NEO4J_URI",
    "CLUSTER_LEVEL",
    "RAG_METHOD",
    "VECTORSTORE",
    "CHROMA_PATH",
    "MILVUS_URI",
    "MILVUS_TOKEN"
]

default_envs = {
    "OPENAI_BASE_URL":"http://localhost:8000/v1",
    "OPENAI_API_KEY":"0",
    "DEFAULT_EMBED_MODEL":"text-embedding-ada-002",
    "DEFAULT_CHAT_MODEL":"gpt-4o-mini",
    "HF_TOKENIZER_PATH":"01-ai/Yi-6B-Chat",
    "DEFAULT_CHUNK_SIZE":"300",
    "DEFAULT_CHUNK_OVERLAP":"30",
    "RETRIEVER":"dense",
    "RERANKER":"None",
    "STORAGE":"redis",
    "SEARCH_TARGET":"content",
    "REDIS_URI":"redis://localhost:6379",
    "ELASTICSEARCH_URI":"http://localhost:9001",
    "GRAPH_STORAGE": "None",
    "NEO4J_URI": "bolt://localhost:7687",
    "CLUSTER_LEVEL": "1",
    "RAG_METHOD": "naive",
    "VECTORSTORE":"chroma",
    "CHROMA_PATH":"./chroma",
    "MILVUS_URI":"http://localhost:19530",
    "MILVUS_TOKEN":"0"
}

def init_env():
    for key, value in default_envs.items():
        if key not in os.environ:
            os.environ[key] = value

def save_to_env(name, value):
    if name == "naive":
        os.environ["RERANKER"] = value
    elif name == "graph":
        os.environ["CLUSTER_LEVEL"] = value
    else:
        os.environ[name] = str(value)


def save_storage_path(value):
    storage = os.environ['STORAGE']
    if storage == 'redis':
        os.environ['REDIS_URI'] = value
    elif storage == 'es':
        os.environ['ELASTICSEARCH_URI'] = value

def get_storage_path():
    storage = os.environ['STORAGE']
    storage_path = None
    if storage == 'redis':
        storage_path = os.environ['REDIS_URI']
    elif storage == 'es':
        storage_path = os.environ['ELASTICSEARCH_URI']
    return storage_path

def save_graph_storage_path(value):
    graph_storage = os.environ['GRAPH_STORAGE']
    if graph_storage == 'neo4j':
        os.environ['NEO4J_URI'] = value

def get_graph_storage_path():
    graph_storage = os.environ['GRAPH_STORAGE']
    graph_storage_path = None
    if graph_storage == 'neo4j':
        graph_storage_path = os.environ['NEO4J_URI']
    return graph_storage_path
        

def save_vectorstore_path(value, token):
    vectorstore = os.environ['VECTORSTORE']
    if vectorstore == 'chroma':
        os.environ['CHROMA_PATH'] = value
    elif vectorstore == 'milvus':
        os.environ['MILVUS_URI'] = value
        os.environ['MILVUS_TOKEN'] = token
    elif vectorstore == 'es':
        os.environ['ELASTICSEARCH_URI'] = value

def get_vectorstore_path():
    vectorstore = os.environ['VECTORSTORE']
    vectorstore_path = None
    vectorstore_token = None
    if vectorstore == 'chroma':
        vectorstore_path = os.environ['CHROMA_PATH']
    elif vectorstore == 'milvus':
        vectorstore_path = os.environ['MILVUS_URI']
        vectorstore_token = os.environ['MILVUS_TOKEN']
    elif vectorstore == 'es':
        vectorstore_path = os.environ['ELASTICSEARCH_URI']
    return vectorstore_path, vectorstore_token

def save_as_dotenv():
    with open(".env", "w") as f:
        for env in envs_to_save:
            f.write(f"{env}={os.getenv(env)}\n")
            