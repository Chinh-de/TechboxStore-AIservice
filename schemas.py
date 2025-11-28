from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: List[ChatMessage] = []

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10

class RecRequest(BaseModel):
    spus: List[str]
    top_k: int = 10