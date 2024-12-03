from cardinal.model import EmbedOpenAI
def rerank(docs):
    contents = [doc["content"] for doc in docs]
    embedding_model = EmbedOpenAI()
    embeddings = embedding_model.batch_embed(contents)
    print(embeddings)
    return docs