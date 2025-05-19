from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey, Enum, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import Enum as SQLAlchemyEnum

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(80), nullable=False)
    lastname: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    posts: Mapped[list['Post']] = relationship(back_populates="user")
    comments: Mapped[list['Comment']] = relationship(back_populates="author")
    following: Mapped[list['Follower']] = relationship(foreign_keys='Follower.user_from_id', back_populates="follower")
    followers: Mapped[list['Follower']] = relationship(foreign_keys='Follower.user_to_id', back_populates="following_user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "is_active": self.is_active
            # No serializamos la contraseña por seguridad
        }

    def __repr__(self):
        return f"<User(username='{self.username}')>"

class Post(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str | None] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    user: Mapped['User'] = relationship(back_populates="posts")
    media: Mapped[list['Media']] = relationship(back_populates="post")
    comments: Mapped[list['Comment']] = relationship(back_populates="post")

    def __repr__(self):
        return f"<Post(id={self.id}, content='{self.content[:20]}...')>"

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "user_id": self.user_id
        }

class MediaType(enum.Enum):
    IMAGE = 'image'
    VIDEO = 'video'

class Media(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[MediaType] = mapped_column(SQLAlchemyEnum(MediaType), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable=False)

    post: Mapped['Post'] = relationship(back_populates="media")

    def __repr__(self):
        return f"<Media(id={self.id}, type='{self.type}', url='{self.url}')>"

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "url": self.url,
            "post_id": self.post_id
        }

class Comment(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment_text: Mapped[str] = mapped_column(String(255), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable=False)

    author: Mapped['User'] = relationship(back_populates="comments")
    post: Mapped['Post'] = relationship(back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, comment='{self.comment_text[:20]}...')>"

    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "author_id": self.author_id,
            "post_id": self.post_id
        }

from sqlalchemy import PrimaryKeyConstraint

class Follower(db.Model):
    user_from_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    user_to_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)

    follower: Mapped['User'] = relationship(foreign_keys=[user_from_id], back_populates="following")
    following_user: Mapped['User'] = relationship(foreign_keys=[user_to_id], back_populates="followers")

    __table_args__ = (
        PrimaryKeyConstraint('user_from_id', 'user_to_id'),
    )

    def __repr__(self):
        return f"<Follower(follower_id={self.user_from_id}, following_id={self.user_to_id})>"

    def serialize(self):
        return {
            "follower_id": self.user_from_id,
            "following_id": self.user_to_id
        }