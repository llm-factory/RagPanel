from cardinal import AutoStorage, AutoVectorStore
from types import DocIndex, Document


if __name__ == '__main__':
    storage = AutoStorage[Document](name='test')
    vectorstore = AutoVectorStore[DocIndex](name='test')
    # TODO