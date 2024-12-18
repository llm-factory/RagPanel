# RagPanel
[English | [简体中文](README_zh.md)]
## 📄Introduction
Rag Panel is an open source RAG rapid deployment project, including visual interactive interface and API calls.
## 🚀Quick Start
0. Prepare a chat model and an embedding model. Closed source models are recommended to use [One API](https://github.com/songquanpeng/one-api) to access (OpenAI API is also OK). Open source models are recommended to use [imitater](https://github.com/the-seeds/imitater) to access.
1. Clone git and create conda environment:
```
git clone https://github.com/the-seeds/RagPanel
cd RagPanel
conda create -n ragpanel python=3.10
conda activate ragpanel
```
2. Start database server, including a kv storage server and a vector storage server (**and a graph storage for GraphRAG**).We recommend deploy them using docker and we have provided docker compose file in [docker](docker) folder. Take `redis` as an example, you can run following command to start `redis`:
```
cd docker/redis
docker compose up -d
```
&emsp;&emsp;Supported kv storages: `redis`,  `elasticsearch`.  
&emsp;&emsp;Supported vector storages: `chroma`, `milvus`.  
&emsp;&emsp;Supported graph storages: `neo4j`.  
&emsp;&emsp;`chroma` only needs to follow later steps to install the python dependencies to run and don't need docker.
> [!NOTE] 
> Pulling docker image is sometimes unstable and maybe you need proxy. Besides, you can also install redis by [source code](https://github.com/redis/redis?tab=readme-ov-file#installing-redis). Then you can start `redis` + `chroma` without docker.

3. Install dependencies according to your database server. Again we take `redis`+`chroma`+`neo4j` as an example:
```
pip install -e ".[redis, chroma, neo4j]"
```  

4. Run `ragpanel-cli --action webui`, and choose language `en` (English) or `zh` (Chinese) to start a Web UI like:
![Web UI](assets/webui.png)

## 📡Api Example
Create a `.env` and a `config.yaml` as follows: 
> [!Note]
> If you have used Web UI, the data you filled in the UI will be saved as `.env` and `config.yaml` automatically when you click `save and apply` button
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
Assuming you have created **.env** and **config.yaml** properly, and **started your database server**, you can see README in [examples/api](examples/api/) folder to know how to start and use API server.

## 📚Graph RAG
![graphrag](assets/graphrag.png)
Our GraphRAG implementation is shown in the figure. First we use LLM to extract entities and relations from docs, and summarize similar entities or relations. Then we insert these elements into graph storage and get the knowledge graph. Next, we use Leiden clustering to get a graph community. And finally we use LLM to generate community reports and store them.  
When one query is given, we will first retrieve related entities in vector storage, and then query communities the entities belong to. In the end, we query reports of communities in KV storage as the retrieval results. 

## 🗄Database
![database](assets/database_usage.png)  
The data storage usage is shown in the figure above. This project supports sparse retrieval and dense retrieval: sparse retrieval searches the document content in the KV database and directly obtains the document content; dense retrieval searches in the vector store and obtains the document block id, and then get the document content from the KV database.