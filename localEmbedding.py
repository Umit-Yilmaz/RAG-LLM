from langchain_community.embeddings.ollama import OllamaEmbeddings


def localEmbedding():
    # local embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings

# author: Umit-Yilmaz
