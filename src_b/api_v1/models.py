from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone, timedelta
import hashlib

DATABASE_URL = "sqlite:///./forum.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def now_rounded_to_minute():
    dt = datetime.now(timezone.utc)
    return dt.replace(second=0, microsecond=0)


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=now_rounded_to_minute)
    posts = relationship("Post", back_populates="topic")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=now_rounded_to_minute)
    topic = relationship("Topic", back_populates="posts")


def init_db():
    Base.metadata.create_all(bind=engine)


ADMIN_TOKEN_HASH = "7d80b93a8bd6dc67fea7f89555da1d0b60356863290ca5668160d6d97fe90f75"


def check_admin_token(token: str) -> bool:
    return hashlib.sha256(token.encode()).hexdigest() == ADMIN_TOKEN_HASH


class BannedUser(Base):
    __tablename__ = "banned_users"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, nullable=False)
    banned_at = Column(DateTime, default=now_rounded_to_minute)


def is_banned(ip_address: str) -> bool:
    db = SessionLocal()
    banned = db.query(BannedUser).filter(
        BannedUser.ip_address == ip_address).first()
    db.close()
    return banned is not None


def ban_user(ip_address: str):
    db = SessionLocal()
    if not db.query(BannedUser).filter(BannedUser.ip_address == ip_address).first():
        banned = BannedUser(ip_address=ip_address)
        db.add(banned)
        db.commit()
    db.close()
