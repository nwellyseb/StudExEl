"""
Message model.

Stores one private message sent inside a marketplace conversation.
"""

from datetime import datetime

from extensions import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversations.id"),
        nullable=False,
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    body = db.Column(
        db.Text,
        nullable=False,
    )

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    conversation = db.relationship(
        "Conversation",
        back_populates="messages",
    )

    sender = db.relationship(
        "User",
        back_populates="sent_messages",
    )

    __table_args__ = (
        db.Index(
            "ix_messages_conversation_created_at",
            "conversation_id",
            "created_at",
        ),
    )
