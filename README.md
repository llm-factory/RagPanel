# RagPanel
## Quick Start
 1. Install [cardinal](https://github.com/the-seeds/cardinal.git) with
 ```
    git clone https://github.com/the-seeds/cardinal.git
    pip install -e .
    pip install -r requirements-dev.txt
 ```

2. Start database server, including a storage server and a vectorstore server.  
Supported storages: `redis`,  `elasticsearch`.  
Supported vectorstores: `chroma`, `milvus`.

3. Create a `.env` and a `config.yaml` as follows:

```
# .env
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

```
# config.yaml
build:
  database: init
  folder: input

launch:
  database: init
  host: 127.0.0.1
  port: 8000

dump:
  database: init
  folder: output
```

4. Run `python launch.py`, and then choose your action and fill the path of your config file.  

   You can also directly run `python launch.py --action YOUR_ACTION --config CONFIG_FILE` to start. Here are action choices:  
   `build`: read data, split docs and build index.  
   `launch`: launch app server.  
   `dump`: dump chat history.  
   `webui`: visual webui (driven by Gradio).
   
## Web UI
You can start a webui server to set and test your environment as follows:
1. Run `python launch.py --action webui`. You will see ui like:
![Web UI](./assets/webui.png)

2. Set proper parameters and then try to insert, retrieve and chat to check your environment.
