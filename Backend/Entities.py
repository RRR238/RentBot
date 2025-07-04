from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,BigInteger, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import class_mapper
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String, unique=True, index=True)

    chat_sessions = relationship("Chat_session", back_populates="user")

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in class_mapper(self.__class__).columns}


class Chat_session(Base):
    __tablename__ = 'chat_sessions'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_interaction = Column(DateTime(timezone=True),default=datetime.utcnow, server_default=func.now(),nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"))
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="chat_sessions")
    chat_history = relationship('Chat_history',back_populates='chat_session')


class Chat_history(Base):
    __tablename__ = 'chat_histories'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey('chat_sessions.id', ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(String)
    message = Column(String)

    chat_session = relationship("Chat_session", back_populates="chat_history")