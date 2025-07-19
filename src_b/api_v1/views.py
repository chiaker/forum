from fastapi import APIRouter, HTTPException, Query
from .schemas import Topic, TopicCreate, Post, PostCreate
from . import crud
from src_b.api_v1.models import check_admin_token

router = APIRouter()


@router.get("/topics", response_model=list[Topic])
def get_topics():
    return crud.get_all_topics()


@router.get("/topics/{topic_id}", response_model=Topic)
def get_topic(topic_id: int):
    topic = crud.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.post("/topics", response_model=Topic)
def create_topic(topic: TopicCreate):
    return crud.create_topic(topic)


@router.delete("/topics/{topic_id}", response_model=Topic)
def delete_topic(topic_id: int, admin_token: str = Query(...)):
    if not check_admin_token(admin_token):
        raise HTTPException(status_code=403, detail="Нет прав администратора")
    topic = crud.delete_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Топик не найден")
    return topic


@router.get("/topics/{topic_id}/posts", response_model=list[Post])
def get_posts(topic_id: int):
    posts = crud.get_posts_by_topic(topic_id)
    return posts


@router.post("/topics/{topic_id}/posts", response_model=Post)
def create_post(topic_id: int, post: PostCreate):
    created_post = crud.create_post(topic_id, post)
    if not created_post:
        raise HTTPException(status_code=404, detail="Топик не найден")
    return created_post


@router.get("/topics/{topic_id}/posts/{post_id}", response_model=Post)
def get_post_by_id(post_id: int):
    post = crud.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return post


@router.delete("/topics/{topic_id}/posts/{post_id}", response_model=Post)
def delete_post_by_topic(topic_id: int, post_id: int, admin_token: str = Query(...)):
    if not check_admin_token(admin_token):
        raise HTTPException(status_code=403, detail="Нет прав администратора")
    post = crud.delete_post_by_topic(topic_id, post_id)
    if not post:
        raise HTTPException(
            status_code=404, detail="Пост не найден в этом топике")
    return post
