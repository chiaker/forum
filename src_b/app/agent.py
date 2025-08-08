import json
import random
import threading
import time
import urllib.request
from datetime import datetime, timedelta, timezone

from src_b.app.config import AI_ENABLED, AI_BASE_URL, AI_MODEL, AI_MIN_DELAY_MINUTES, AI_MAX_DELAY_MINUTES
from src_b.api_v1.models import SessionLocal, Topic, Post, AiAgentState


def _now():
    return datetime.now(timezone.utc)


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
    return (
        "Ты выступаешь в роли участника форума. Ответь кратко, по делу, дружелюбно, без преамбулы и без повторов вопроса. "
        "Опирайся на тему и последние сообщения. Пиши сплошным текстом. Максимум 150 символов.\n\n"
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
    state = _ensure_state(db, topic_id)
    last_post = (
        db.query(Post)
        .filter(Post.topic_id == topic_id)
        .order_by(Post.created_at.desc())
        .first()
    )
    base_time = last_post.created_at if last_post else _now()
    state.last_post_at = base_time
    next_due = base_time + _random_delay()
    if next_due < _now():
        next_due = _now() + _random_delay()
    state.next_due_at = next_due
    db.add(state)
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
