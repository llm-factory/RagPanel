from typing import TYPE_CHECKING, Generator, Sequence

from cardinal import AssistantMessage, AutoStorage, BaseCollector, ChatOpenAI, DenseRetriever, HumanMessage, Template

from .protocol import DocIndex, Document, History


if TYPE_CHECKING:
    from cardinal import BaseMessage


class ChatEngine:
    def __init__(self, database: str) -> None:
        self._window_size = 6
        self._chat_model = ChatOpenAI()
        self._collector = BaseCollector[History](storage_name=database)
        self._retriever = DenseRetriever[DocIndex](vectorstore_name=database, threshold=1.0, verbose=True)
        self._storage = AutoStorage[Document](name=database)
        self._kbqa_template = Template("充分理解以下事实描述：{context}\n\n回答下面的问题：{query}")

    def stream_chat(self, messages: Sequence["BaseMessage"], **kwargs) -> Generator[str, None, None]:
        messages = messages[-(self._window_size * 2 + 1) :]
        query = messages[-1].content

        indexes = self._retriever.retrieve(query, top_k=2)
        documents = [self._storage.query(index.doc_id).content for index in indexes]
        if len(documents):
            query = self._kbqa_template.apply(context="\n".join(documents), query=query)

        augmented_messages = messages[:-1] + [HumanMessage(content=query)]
        response = ""
        for new_token in self._chat_model.stream_chat(augmented_messages, **kwargs):
            yield new_token
            response += new_token

        self._collector.collect(History(messages=(augmented_messages + [AssistantMessage(content=response)])))
