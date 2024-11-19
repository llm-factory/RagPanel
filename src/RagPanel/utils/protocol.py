import time
import uuid
from enum import IntEnum
from typing import List, Literal, Optional, Union
from cardinal import BaseMessage, Role
from pydantic import BaseModel, Field


class Text:
    def __init__(self, filepath:str, contents:str) -> None:
        self.filepath = filepath
        self.contents = contents
    
    
class CSV():
    def __init__(self, filepath:str, keys, contents) -> None:
        self.filepath = filepath
        self.keys = keys
        self.contents = contents
        
        
class DocIndex(BaseModel):
    doc_id: str = Field(default_factory=lambda: uuid.uuid4().hex)


class Document(DocIndex):
    content: str


class History(BaseModel):
    messages: List[BaseMessage]


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-3.5-turbo"
    messages: List[BaseMessage]
    temperature: float = 0.9
    max_tokens: int = 2048
    stream: bool = False


class ChatCompletionMessage(BaseModel):
    role: Optional[Role] = None
    content: Optional[str] = None


class ChatCompletionResponseChoice(BaseModel):
    index: int = 0
    message: ChatCompletionMessage
    finish_reason: str = "stop"


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int = 0
    delta: ChatCompletionMessage
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    id: Literal["chatcmpl-default"] = "chatcmpl-default"
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = "gpt-3.5-turbo"
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]


class ModelCard(BaseModel):
    id: str = "gpt-3.5-turbo"
    object: Literal["model"] = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: Literal["owner"] = "owner"


class ModelList(BaseModel):
    object: Literal["list"] = "list"
    data: List[ModelCard] = []

class Operator(IntEnum):
    Eq = 0
    Ne = 1
    Gt = 2
    Ge = 3
    Lt = 4
    Le = 5
    In = 6
    Notin = 7
    And = 8
    Or = 9
