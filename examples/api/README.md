## Usage
[English | [简体中文](README_zh.md)]
### Build index
Building index includes load files, split files, embed chunks and insert to database. With proper config, you can run `ragpanel-cli --action build --config ./config/config.yaml` to start building index.  
Tokenizer、Embedding Model、database are set in `.env`:
```
DEFAULT_EMBED_MODEL=text-embedding-ada-002
HF_TOKENIZER_PATH=01-ai/Yi-6B-Chat
...
```
Database collection and data folder are set in `config.yaml`:
```
database:
  collection: init

build:
  folder: ./examples/inputs
```
You would see following outputs:
```
loading splitter...
Extract content: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 24.64it/s]
Split content: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  3.38it/s]
Build index: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:03<00:00,  3.24s/it]
11/25/2024 21:07:48 - INFO - RagPanel.engines.api_engine - Build completed.
```

### Launch API
After building index, you can launch API server with `ragpanel --action launch --config ./config/config.yaml`. You would see:
```
INFO:     Started server process [10455]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
```
Host and port are set in `config.yaml`:
```
launch:
  host: 127.0.0.1
  port: 8080
```

### Chat with API
After launching api server, you can post to the url like `post.py`. You will receive response from the model like:
```
Yes, according to the context provided, Trump won the 2024 election as the nominee of the Republican Party and is now the president-elect of the United States.
```  
This answer is based on the doc in `inputs` folder, because most models don't know about the 2024 US election as their knowledge are behind the news.

### Dump Chat History
You can run `ragpanel-cli --action dump --config ./config/config.yaml` to dump your chat history to the folder set in `config.yaml`:
```
dump:
  folder: ./examples/chat_history
```
In fact, chat history are stored in the `history_{chat_collection}` collection in KV storage and you can view directly.