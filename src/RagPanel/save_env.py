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
    "SEARCH_TARGET",
    "REDIS_URI",
    "ELASTICSEARCH_URI",
    "VECTORSTORE",
    "CHROMA_PATH",
    "MILVUS_URI",
    "MILVUS_TOKEN"
]


def save_to_env(name, value):
    os.environ[name] = str(value)


def save_as_dotenv():
    with open(".env", "w") as f:
        for env in envs_to_save:
            f.write(f"{env} = {os.environ[env]}\n")
            