import uuid
from fastapi import APIRouter, HTTPException, Query, Request, Response, Cookie
from .schemas import Topic, TopicCreate, Post, PostCreate
from . import crud
from src_b.api_v1.models import check_admin_token

router = APIRouter()


def censor_check(text: str) -> bool:
    forbidden_words = ["казино", "криптовалюта", "крипта"]
    for word in forbidden_words:
        if word in text.lower():
            return True
    return False


def get_user_id(request: Request, user_id: str = Cookie(default=None)):
    if user_id is None:
        # Генерируем новый UUID
        user_id = str(uuid.uuid4())
    return user_id


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
def create_topic(topic: TopicCreate, request: Request, response: Response, user_id: str = Cookie(default=None)):
    user_id = get_user_id(request, user_id)

    if user_id not in request.cookies:
        response.set_cookie(key="user_id", value=user_id,
                            httponly=True, max_age=60*60*24*365)
    if crud.is_user_banned(user_id):
        raise HTTPException(status_code=403, detail="Вы забанены")
    if censor_check(topic.title) or censor_check(topic.content):
        crud.ban_user(user_id)
        raise HTTPException(
            status_code=403, detail="Вы забанены за использование запрещённых слов")

    if not topic.title or topic.title.strip() == "":
        raise HTTPException(
            status_code=422, detail="Название топика не может быть пустым")
    if not topic.content or topic.content.strip() == "":
        raise HTTPException(
            status_code=422, detail="Текст топика не может быть пустым")

    if len(topic.title) > 40:
        raise HTTPException(
            status_code=422, detail="Название топика не может быть длиннее 40 символов")

    if len(topic.content) > 3000:
        raise HTTPException(
            status_code=422, detail="Текст топика не может быть длиннее 3000 символов")

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
def create_post(topic_id: int, post: PostCreate, request: Request, response: Response, user_id: str = Cookie(default=None)):
    user_id = get_user_id(request, user_id)

    if user_id not in request.cookies:
        response.set_cookie(key="user_id", value=user_id,
                            httponly=True, max_age=60*60*24*365)
    if crud.is_user_banned(user_id):
        raise HTTPException(status_code=403, detail="Вы забанены")
    if censor_check(post.content):
        crud.ban_user(user_id)
        raise HTTPException(
            status_code=403, detail="Вы забанены за использование запрещённых слов")

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
