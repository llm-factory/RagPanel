import uuid
from typing import List
from cardinal import BaseMessage
from pydantic import BaseModel, Field
from cardinal.vectorstore.schema import Operator


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
    