from pydantic import BaseModel
from datetime import datetime


class Comment(BaseModel):
    id: int
    topic_id: int
    content: str
    created_at: str
    author: str


class TopicCreate(BaseModel):
    title: str


class Topic(BaseModel):
    id: int
    title: str
    created_at: datetime


class PostCreate(BaseModel):
    topic_id: int
    content: str


class Post(BaseModel):
    id: int
    topic_id: int
    content: str
    created_at: datetime
