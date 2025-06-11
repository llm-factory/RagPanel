import gradio as gr
import pandas as pd
from typing import TYPE_CHECKING, Generator, Sequence
from cardinal import AssistantMessage, ChatOpenAI, HumanMessage, Template
from ..utils.protocol import History

if TYPE_CHECKING:
    from cardinal import BaseMessage
    

class ChatEngine:
    def __init__(self, engine, name) -> None:
        self.engine = engine
        self.chat_model = None
        self.name = name
        self.kbqa_template = Template("Based on the following context:{context}\n\nAnswer this question:{query}")
        self.window_size = 6
        self.top_k = 2
        self.threshold = 1.0
        self.with_doc = False
        self.reranker = "None"
        self.show_docs = True
        self.save_history = True
        
    def update(self, template, show_docs, save_history):
        self.kbqa_template = Template(template)
        self.show_docs = show_docs
        self.save_history = save_history
    
    def get_search_results(self):
        return self.search_results
            
    def stream_chat(self, messages: Sequence["BaseMessage"], **kwargs) -> Generator[str, None, None]:
        if self.chat_model is None:
            self.chat_model = ChatOpenAI()
        messages = messages[-(self.window_size * 2 + 1) :]
        query = messages[-1].content

        docs = self.engine.search(query=query, threshold=self.threshold, top_k=self.top_k, reranker=self.reranker)
        if len(docs):
            docs = [doc["content"] for doc in docs]
            query = self.kbqa_template.apply(context="\n".join(docs), query=query)

        augmented_messages = messages[:-1] + [HumanMessage(content=query)]
        response = ""
        for new_token in self.chat_model.stream_chat(augmented_messages, **kwargs):
            yield new_token
            response += new_token

    def retrieve(self, query, enable):
        if enable:
            gr.Info("正在检索文档...")
            return self.engine.search(query=query)
        else:
            return pd.DataFrame([])
         
    def ui_chat(self, conversations, docs):
        query = conversations[-1]["content"]
        if self.chat_model is None:
            self.chat_model = ChatOpenAI()
        history = History(messages=[])
        for conversation in conversations[:-1]:
            if conversation["role"] == "user":
                history.messages.append(HumanMessage(content=conversation["content"]))
            else:
                history.messages.append(AssistantMessage(content=conversation["content"]))

        if len(docs):
            docs = docs["content"].tolist()
            query = self.kbqa_template.apply(context="\n".join(docs), query=query)
            conversations[-1]["content"] = query

        history.messages.append(HumanMessage(content=query))
        conversations += [{"role": "assistant", "content": ""}]
        for new_token in self.chat_model.stream_chat(messages=history.messages):
            conversations[-1]["content"] += new_token
            yield conversations
        history.messages.append(AssistantMessage(content=conversations[-1]["content"]))
