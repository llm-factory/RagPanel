# RagPanel
[English | [简体中文](README_zh.md)]
## Quick Start
1. Start database server, including a storage server and a vectorstore server.  
Supported storages: `redis`,  `elasticsearch`.  
Supported vectorstores: `chroma`, `milvus`.  
You can deploy them using docker. (See [docker](docker/) folder)
![database](assets/database.png)

2. Install dependencies according to your database server. Take `elasticsearch`+`milvus` as an example:
```
git clone https://github.com/the-seeds/RagPanel
cd RagPanel
pip install -e ".[es, milvus]"
```

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
database:
  collection: init

build:
  folder: ./examples/inputs

launch:
  host: 127.0.0.1
  port: 8080

dump:
  folder: ./examples/chat_history
```

4. Run `ragpanel-cli --action YOUR_ACTION --config CONFIG_FILE` to start.  
Here are action choices:  
`build`: read data, split docs and build index.  
`launch`: launch app server.  
`dump`: dump chat history.  
`webui`: visual webui (driven by Gradio).

## Api Example
Assuming you have created **.env** and **config.yaml** properly, and **started your database server**, take data in [examples](examples) folder as an example.  
1. Run `ragpanel-cli --action build --config examples/config/config.yaml` to build index.  
2. Run `ragpanel-cli --action launch --config examples/config/config.yaml` to launch api service.
3. Send post to server like [post.py](examples/post.py). You can run `python examples/post.py` to test.  
4. Run `ragpanel-cli --action dump --config examples/config/config.yaml` to dump your chat history if needed.  
You can see README in [examples](examples) folder for more details.
   
## Web UI
You can start a webui server to set and test your environment as follows:
1. Run `ragpanel-cli --action webui`. You will see ui like:
![Web UI](assets/webui.png)

2. Set proper parameters and then try to insert, retrieve and chat to check your environment.

## Local Model Support
Our framework only supports API calls, so if you would like to use local model, you can run [imitater](https://github.com/the-seeds/imitater) to convert local model to a form that supports the OpenAI API.