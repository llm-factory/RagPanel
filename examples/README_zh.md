## 使用
### 索引构建
索引构建部分包括加载文件、文档分块、文档嵌入和插入数据库，设置妥当后，您可以运行`ragpanel-cli --action build --config ./config/config.yaml`来启动索引构建工作。  
分词器、词嵌入模型、数据库类型等在`.env`中设置：
```
DEFAULT_EMBED_MODEL=text-embedding-ada-002
HF_TOKENIZER_PATH=01-ai/Yi-6B-Chat
...
```
数据库集合和待载入数据文件夹在`config.yaml`中设置：
```
database:
  collection: init

build:
  folder: ./examples/inputs
```
运行后，您会看到如下输出:
```
loading splitter...
Extract content: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 24.64it/s]
Split content: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  3.38it/s]
Build index: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:03<00:00,  3.24s/it]
11/25/2024 21:07:48 - INFO - RagPanel.engines.api_engine - Build completed.
```

### 启动API
构建索引完毕后，您可以启动API服务了，运行`ragpanel --action launch --config ./config/config.yaml`即可。您会看到如下输出：
```
INFO:     Started server process [10455]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
```
您可以更改`config.yaml`中的host和port设置:
```
launch:
  host: 127.0.0.1
  port: 8080
```

### 使用API聊天
启动API后，您可以像`post.py`中的代码一样发送post请求，并收到来自模型的RAG回复，例如：
```
Yes, according to the context provided, Trump won the 2024 election as the nominee of the Republican Party and is now the president-elect of the United States.
```
这个回答显然是基于`inputs`中的文档的，因为大部分大模型的知识截止在美国2024大选之前，无法准确回答该问题。

### 导出聊天记录
您可以运行`ragpanel-cli --action dump --config ./config/config.yaml`来导出聊天记录到`config.yaml`中设置的文件夹:
```
dump:
  folder: ./examples/chat_history
```
事实上，聊天记录均存储在KV数据库中的`history_{chat_collection}`集合中，您也可以通过查看数据库内容来查看聊天记录。