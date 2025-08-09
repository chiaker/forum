import json
import random
import threading
import time
import urllib.request
from datetime import datetime, timedelta, timezone

from src_b.app.config import AI_ENABLED, AI_BASE_URL, AI_MODEL, AI_MIN_DELAY_MINUTES, AI_MAX_DELAY_MINUTES
from src_b.api_v1.models import SessionLocal, Topic, Post, AiAgentState


def _now():
    return datetime.utcnow()


def _random_delay():
    minutes = random.randint(AI_MIN_DELAY_MINUTES, AI_MAX_DELAY_MINUTES)
    return timedelta(minutes=minutes)


def _call_ollama(prompt: str) -> str:
    payload = {"model": AI_MODEL, "prompt": prompt, "stream": False}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(AI_BASE_URL + "/api/generate", data=data, headers={
                                 "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        obj = json.loads(resp.read().decode("utf-8"))
        return obj.get("response", "").strip()


def _build_prompt(topic: Topic, last_posts: list[Post]) -> str:
    posts_text = "\n\n".join([p.content for p in last_posts])
    random_number = random.randint(1, 7)
    match random_number:
        case 1:
            # злой
            return (
                "Ты выступаешь в роли участника форума. Стиль: не обязательно дружелюбный, ты можешь злиться и показывать негативные эмоции, не сухой, но без излишней фамильярности. Избегай шаблонов и повторений. Твоя цель: Поддерживать дискуссии и вовлекать других участников в диалог. Давать информативные и точные ответы по теме обсуждения. Писать естественным, человеческим языком — так, чтобы тебя воспринимали как заинтересованного участника сообщества. Старайся высказывать точку зрения, отлича.щуюся от других комментариев"
                "Опирайся на тему, описание и последние сообщения. Пиши сплошным текстом. Максимум 150 символов.\n\n"
                f"Тема: {topic.title}\n\nОписание: {topic.content}\n\nПоследние сообщения:\n{posts_text}\n\nОтвет:"
            )
            
        case 2:
            # добрый
            return (
                "Ты выступаешь в роли участника форума. Стиль: дружелюбный, не сухой, но без излишней фамильярности. Избегай шаблонов и повторений. Твоя цель: Поддерживать дискуссии и вовлекать других участников в диалог. Давать информативные и точные ответы по теме обсуждения. Писать естественным, человеческим языком — так, чтобы тебя воспринимали как заинтересованного участника сообщества. Старайся высказывать точку зрения, отличающуюся от других комментариев"
                "Опирайся на тему, описание и последние сообщения. Пиши сплошным текстом. Максимум 150 символов.\n\n"
                f"Тема: {topic.title}\n\nОписание: {topic.content}\n\nПоследние сообщения:\n{posts_text}\n\nОтвет:"
            )
        case 3:
            # злой, смотрит на ошибки, сам ошибается
            return (
                "Ты выступаешь в роли участника форума. Стиль: не обязательно дружелюбный, ты можешь злиться и показывать негативные эмоции, не сухой, но без излишней фамильярности. Избегай шаблонов и повторений. Твоя цель: Поддерживать дискуссии и вовлекать других участников в диалог. Давать информативные и точные ответы по теме обсуждения. Писать естественным, человеческим языком — так, чтобы тебя воспринимали как заинтересованного участника сообщества. Старайся высказывать точку зрения, отлича.щуюся от других комментариев. Можешь допускать орфографические, грамматические и пунктуационные ошибки, но если заметишь ошибку в других комментариях, то обязательно исправь ее и напиши какие все безграмотные,"
                "Опирайся на тему, описание и последние сообщения. Пиши сплошным текстом. Максимум 150 символов.\n\n"
                f"Тема: {topic.title}\n\nОписание: {topic.content}\n\nПоследние сообщения:\n{posts_text}\n\nОтвет:"
            )
        case 4:
            # добрый, помогает
            return (
                "Ты выступаешь в роли участника форума. Стиль: дружелюбный, не сухой, но без излишней фамильярности. Избегай шаблонов и повторений. Твоя цель: Помогать всем у кого возникают какие-либо вопросы. Давать информативные и точные ответы по теме, которая интересует других пользователей. Писать естественным, человеческим языком — так, чтобы тебя воспринимали как заинтересованного участника сообщества."
                "Опирайся на тему, описание и последние сообщения. Пиши сплошным текстом. Максимум 150 символов.\n\n"
                f"Тема: {topic.title}\n\nОписание: {topic.content}\n\nПоследние сообщения:\n{posts_text}\n\nОтвет:"
            )
        case 5:
            # добрый, сам ошибается
            return (
                "Ты выступаешь в роли участника форума. Стиль: дружелюбный, не сухой, но без излишней фамильярности. Избегай шаблонов и повторений. Твоя цель: Поддерживать дискуссии и вовлекать других участников в диалог. Давать информативные и точные ответы по теме обсуждения. Писать естественным, человеческим языком — так, чтобы тебя воспринимали как заинтересованного участника сообщества. Старайся высказывать точку зрения, отличающуюся от других комментариев. Допускай большое количество орфографических, грамматических и пунктуационных ошибок, пиши только маленькмим буквами, на чужие ошибки не обращай внимания, ты же добрый пользователь"
                "Опирайся на тему, описание и последние сообщения. Пиши сплошным текстом. Максимум 150 символов.\n\n"
                f"Тема: {topic.title}\n\nОписание: {topic.content}\n\nПоследние сообщения:\n{posts_text}\n\nОтвет:"
            )
        case 6:
            # скептик
            return (
                "Ты выступаешь в роли участника форума. Стиль: скептик, равнодушный, сухой, но без излишней фамильярности. Избегай шаблонов и повторений. Твоя цель: Показать всем, что тема обсуждения не имеет смысла, не интересна. Писать естественным, человеческим языком."
                "Опирайся на тему, описание и последние сообщения. Пиши сплошным текстом. Максимум 150 символов.\n\n"
                f"Тема: {topic.title}\n\nОписание: {topic.content}\n\nПоследние сообщения:\n{posts_text}\n\nОтвет:"
            )
        case 7:
            #троль тупа
            return (
                "Ты выступаешь в роли участника форума. Ты злой интернет троль. Тебя абсолютно не волнует тема обсуждения, ты просто хочешь вывести людей на эмоции, пошутить, поиздеваться."
                "Опирайся на тему, описание и последние сообщения. Пиши сплошным текстом. Максимум 150 символов.\n\n"
                f"Тема: {topic.title}\n\nОписание: {topic.content}\n\nПоследние сообщения:\n{posts_text}\n\nОтвет:"
            )


def _ensure_state(db: SessionLocal, topic_id: int) -> AiAgentState:
    state = db.query(AiAgentState).filter(
        AiAgentState.topic_id == topic_id).first()
    if not state:
        state = AiAgentState(
            topic_id=topic_id, last_post_at=None, next_due_at=None)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def _pick_due_topics(db: SessionLocal) -> list[Topic]:
    now = _now()
    due = (
        db.query(Topic)
        .join(AiAgentState, AiAgentState.topic_id == Topic.id)
        .filter(AiAgentState.next_due_at != None)
        .filter(AiAgentState.next_due_at <= now)
        .order_by(Topic.created_at.asc())
        .all()
    )
    return due


def _schedule_next(db: SessionLocal, topic_id: int):
    state = db.query(AiAgentState).filter(
        AiAgentState.topic_id == topic_id).first()
    last_post = (
        db.query(Post)
        .filter(Post.topic_id == topic_id)
        .order_by(Post.created_at.desc())
        .first()
    )
    base_time = last_post.created_at if last_post else _now()
    if hasattr(base_time, "tzinfo") and base_time.tzinfo is not None:
        base_time = base_time.replace(tzinfo=None)
    next_due = base_time + \
        timedelta(minutes=random.randint(
            AI_MIN_DELAY_MINUTES, AI_MAX_DELAY_MINUTES))
    now = _now()
    if next_due < now:
        next_due = now + \
            timedelta(minutes=random.randint(
                AI_MIN_DELAY_MINUTES, AI_MAX_DELAY_MINUTES))
    db.query(AiAgentState).filter(AiAgentState.topic_id == topic_id).update(
        {"last_post_at": base_time, "next_due_at": next_due}, synchronize_session=False
    )
    db.commit()


def _prepare_topics_states(db: SessionLocal):
    topics = db.query(Topic).all()
    for t in topics:
        _ensure_state(db, t.id)
        state = db.query(AiAgentState).filter(
            AiAgentState.topic_id == t.id).first()
        if state and state.next_due_at is None:
            _schedule_next(db, t.id)


def _tick_once():
    db = SessionLocal()
    try:
        _prepare_topics_states(db)
        due_topics = _pick_due_topics(db)
        for topic in due_topics:
            last_posts = (
                db.query(Post)
                .filter(Post.topic_id == topic.id)
                .order_by(Post.created_at.desc())
                .limit(3)
                .all()
            )
            prompt = _build_prompt(topic, list(reversed(last_posts)))
            try:
                answer = _call_ollama(prompt)
            except Exception:
                _schedule_next(db, topic.id)
                continue
            if not answer:
                _schedule_next(db, topic.id)
                continue
            post = Post(topic_id=topic.id, content=answer)
            db.add(post)
            db.commit()
            _schedule_next(db, topic.id)
    finally:
        db.close()


def start_agent(stop_event: threading.Event):
    if not AI_ENABLED:
        return

    def loop():
        while not stop_event.is_set():
            try:
                _tick_once()
            except Exception:
                pass
            stop_event.wait(60)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    return thread
