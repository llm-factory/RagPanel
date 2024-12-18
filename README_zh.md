# RagPanel
[[English](README.md) | 简体中文]
## 📄介绍
Rag Panel是一个开源RAG快速部署项目,包含可视化交互界面和API调用。
## 🚀快速开始
0. 准备聊天模型和嵌入模型，闭源模型推荐使用 [One API](https://github.com/songquanpeng/one-api) 接入（也可直接使用OpenAI API），开源模型推荐使用 [imitater](https://github.com/the-seeds/imitater) 接入。
1. 克隆仓库并创建conda环境：
```
git clone https://github.com/the-seeds/RagPanel
cd RagPanel
conda create -n ragpanel python=3.10
conda activate ragpanel
```
2. 启动数据库服务，包括一个键值对数据库和一个向量数据库（和一个图数据库，如果使用GraphRAG）。我们推荐使用docker部署，并在[docker](docker)文件夹下提供了docker compose文件。以`redis`为例，您可以运行以下命令启动`redis`：
```
cd docker/redis
docker compose up -d
```
&emsp;&emsp;目前支持的键值数据库: `redis`,  `elasticsearch`  
&emsp;&emsp;目前支持的向量数据库: `chroma`, `milvus`  
&emsp;&emsp;目前支持的图数据库: `neo4j`  
&emsp;&emsp;`chroma`仅需根据后续步骤安装python依赖即可，无需使用docker运行。
> [!Note]
> docker镜像拉取有时不稳定，您可能需要启动代理。此外，您也可以通过[源码](https://github.com/redis/redis?tab=readme-ov-file#installing-redis)安装redis，来不使用docker完成`redis`+`chroma`的启动。


3. 根据启动的数据库服务安装依赖项。 以 `redis`+`chroma`+`neo4j` 为例:
```
pip install -e ".[redis, chroma, neo4j]"
```

4. 运行 `ragpanel-cli --action webui`来启动Web UI，并根据提示选则英文`en`或中文`zh`。可看到如下界面：  
![Web UI](./assets/webui_zh.png)

## 📡Api服务样例
创建如下的`.env` 和 `config.yaml`文件（如果您使用过Web UI，则可点击其中的`应用并保存`自动生成这两个文件）:
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

# graph storage
GRAPH_STORAGE=neo4j
NEO4J_URI=bolt://localhost:7687
CLUSTER_LEVEL=3

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
  folder: ./inputs

launch:
  host: 127.0.0.1
  port: 8080

dump:
  folder: ./chat_history
```
假设您已经创建完 **.env**和 **config.yaml**，并且**启动了数据库服务**，您可以参考[examples/api](examples/api/)文件夹下的README来启动和使用api服务。  

## 📚Graph RAG
![graphrag](assets/graphrag_zh.png)
我们的GraphRAG实现方式如图所示。首先我们用大模型抽取文档中的实体和关系，并合并相似度过高者，存入图数据库后得到知识图谱。之后我们使用Leiden算法来对知识图谱进行聚类操作，得到图社区。最后我们使用大模型对每个社区生成社区报告，并存入键值数据库。  
在查询时，我们首先在向量数据库中检索最相关的若干实体，并在图数据库中查询到实体所属社区id，从而在键值数据库检索到社区报告，作为检索结果。

## 🗄数据库
![database_zh](assets/database_usage_zh.png)  
数据存储情况如上图所示，本项目支持稀疏检索、稠密检索：稀疏检索在键值数据库中对文档内容检索，直接得到文档内容；稠密检索在向量数据库中检索，得到文档块id，再直接在键值数据库中得到文档内容。