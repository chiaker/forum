from sqlalchemy.orm import Session
from .models import SessionLocal, Topic, Post
from .schemas import TopicCreate, PostCreate


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_all_topics():
    db = SessionLocal()
    topics = db.query(Topic).order_by(Topic.created_at.desc()).all()
    db.close()
    return topics


def create_topic(topic_create: TopicCreate):
    db = SessionLocal()
    topic = Topic(title=topic_create.title)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    db.close()
    return topic


def get_topic(topic_id: int):
    db = SessionLocal()
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    db.close()
    return topic


def get_posts_by_topic(topic_id: int):
    db = SessionLocal()
    posts = db.query(Post).filter(Post.topic_id == topic_id).order_by(
        Post.created_at.asc()).all()
    db.close()
    return posts


def create_post(post_create: PostCreate):
    db = SessionLocal()
    topic = db.query(Topic).filter(Topic.id == post_create.topic_id).first()
    if not topic:
        db.close()
        return None
    post = Post(topic_id=post_create.topic_id, content=post_create.content)
    db.add(post)
    db.commit()
    db.refresh(post)
    db.close()
    return post


def get_post(post_id: int):
    db = SessionLocal()
    post = db.query(Post).filter(Post.id == post_id).first()
    db.close()
    return post


def delete_topic(topic_id: int):
    db = SessionLocal()
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic:
        db.query(Post).filter(Post.topic_id == topic_id).delete()
        db.delete(topic)
        db.commit()
    db.close()
    return topic


def delete_post_by_topic(topic_id: int, post_id: int):
    db = SessionLocal()
    post = db.query(Post).filter(Post.id == post_id,
                                 Post.topic_id == topic_id).first()
    if post:
        db.delete(post)
        db.commit()
    db.close()
    return post
