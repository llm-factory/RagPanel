# RagPanel
[[English](README.md) | 简体中文]
## 快速开始
1. 启动数据库服务，包括一个键值对数据库和一个向量数据库。
目前支持的键值数据库: `redis`,  `elasticsearch`  
目前支持的向量数据库: `chroma`, `milvus`  
您可以使用docker部署 (见[docker](docker)文件夹)
![database_zh](assets/database_zh.png)  
数据存储情况如上图所示，本项目支持稀疏检索、稠密检索：稀疏检索在键值数据库中对文档内容检索，直接得到文档内容；稠密检索在向量数据库中检索，得到文档块id，再直接在键值数据库中得到文档内容。

2. 根据启动的数据库服务安装依赖项。 以 `elasticsearch`+`milvus` 为例:
```
git clone https://github.com/the-seeds/RagPanel
cd RagPanel
pip install -e ".[es, milvus]"
```

3. 创建如下的`.env` 和 `config.yaml`文件（如果您仅使用Web UI，则不需要创建这两个文件，可在UI中配置）:
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

> [!NOTE]
> 闭源模型推荐使用 [One API](https://github.com/songquanpeng/one-api) 接入。
> 
> 开源模型推荐使用 [imitater](https://github.com/the-seeds/imitater) 接入。

```
# config.yaml
database:
  collection: init

build:
  folder: ./inputs

launch:
  host: 127.0.0.1
  port: 8080

dump:
  folder: ./chat_history
```

4. 运行 `ragpanel-cli --action YOUR_ACTION --config CONFIG_FILE_PATH`  
所有行为如下:  
`build`: 读取数据，分割嵌入。  
`launch`: 启动app服务。  
`dump`: 导出聊天历史。  
`webui`: 可视化网页UI (由Gradio驱动)，不需要指定config路径。

## Api服务样例
假设您已经创建完 **.env**和 **config.yaml**，并且**启动了数据库服务**，您可以参考[examples/api](examples/api/)文件夹下的README来启动和使用api服务。  
   
## 网页UI
您可以启动网页UI来设置和测试您的环境配置，如下所示:
1. 运行 `ragpanel-cli --action webui`。之后选择语言`en`（英语）或`zh`（中文），您会看到如下界面：
![Web UI](./assets/webui_zh.png)

2. 设置合适的环境参数，并尝试构建索引、查询、聊天等，以测试环境配置是否有效。
