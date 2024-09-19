from typing import Generator

from cardinal import AssistantMessage, BaseCollector, ChatOpenAI, HumanMessage, Template

from .protocol import History



class ChatEngine:
    def __init__(self, database: str, engine) -> None:
        self._window_size = 6
        self._chat_model = ChatOpenAI()
        self._collector = BaseCollector[History](storage_name=database)
        self._kbqa_template = Template("充分理解以下事实描述：{context}\n\n回答下面的问题：{query}")
        self.engine = engine
        
    def get_history(self):
        histories = self._collector.dump()
        if not len(histories):
            return None
        ret = []
        for history in histories:
            messages = [message.content for message in history.messages]
            ret.append(messages)
        return ret
    
    def stream_chat(self, query, **kwargs) -> Generator[str, None, None]:
        documents = self.engine.search(query, threshold=1, top_k=2)["content"].tolist()
        if len(documents):
            query = self._kbqa_template.apply(context="\n".join(documents), query=query)

        augmented_messages = [HumanMessage(content=query)]
        response = ""
        for new_token in self._chat_model.stream_chat(augmented_messages, **kwargs):
            yield new_token
            response += new_token
        self._collector.collect(History(messages=(augmented_messages + [AssistantMessage(content=response)])))
