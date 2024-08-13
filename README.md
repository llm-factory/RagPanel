# RagPanel
## Usage
install [cardinal](https://github.com/the-seeds/cardinal.git)

install [redis](https://github.com/redis/redis.git) and start server

create a .env
```
# imitater or openai
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=0

# models
DEFAULT_EMBED_MODEL=text-embedding-ada-002
DEFAULT_CHAT_MODEL=gpt-3.5-turbo
HF_TOKENIZER_PATH=01-ai/Yi-6B-Chat

# text splitter
DEFAULT_CHUNK_SIZE=300
DEFAULT_CHUNK_OVERLAP=100

# storages
STORAGE=redis
SEARCH_TARGET=content
REDIS_URI=redis://localhost:6379
ELASTICSEARCH_URI=http://localhost:9001

# vectorstore
VECTORSTORE=chroma
CHROMA_PATH=./chroma
MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=0
```

Run `python launch.py`

## Functions
### Database
Create a new database, clear current database or destroy current database here.
### Insert
Upload your files and they will be splitted, embedded and inserted to database.
### Search
Enter a query, set similarity_threshold and top_k. Related document chunks will be retrieved from database.
### Delete
After searching, you can select from the search result and delete them.
### Launch RAG
Launch the demo in api_demo folder. It is dependent from src.  
You need to choose an action from build (build index with your data), launch (launch RAG chat engine) and dump (dump history).
