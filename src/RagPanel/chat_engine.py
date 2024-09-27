from typing import Generator

from cardinal import AssistantMessage, BaseCollector, ChatOpenAI, HumanMessage, Template

from .protocol import History


class ChatEngine:
    def __init__(self, database: str, engine) -> None:
        self._chat_model = ChatOpenAI()
        self._collector = BaseCollector[History](storage_name=database)
        self._storage_name = database
        self._kbqa_template = Template("充分理解以下事实描述：{context}\n\n回答下面的问题：{query}")
        self.engine = engine
        
    def get_history(self):
        histories = self._collector.dump()
        ret = [[None, "您好，有什么我可以帮助您的吗？"]]
        if not len(histories):
            return ret
        for history in histories:
            messages = [message.content for message in history.messages]
            ret.append(messages)
        return ret
    
    def clear_history(self):
        try:
            self._collector._storage.destroy()
            self._collector = BaseCollector[History](storage_name=self._storage_name)
        except:
            return
    
    def stream_chat(self, history, query, threshold, top_k, template, **kwargs) -> Generator[str, None, None]:
        search_result = self.engine.search(query, threshold=threshold, top_k=top_k)
        if any(search_result):
            documents = search_result["content"].tolist()
            query = Template(str(template)).apply(context="\n".join(documents), query=query)

        augmented_messages = [HumanMessage(content=query)]
        history += [[query, None]]
        history[-1][1] = ""
        for new_token in self._chat_model.stream_chat(augmented_messages, **kwargs):
            history[-1][1] += new_token
            yield history
        self._collector.collect(History(messages=(augmented_messages + [AssistantMessage(content=history[-1][1])])))
