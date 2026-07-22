"""
Conversation model.

Represents a private discussion between a buyer and seller
about one marketplace listing.
"""

from datetime import UTC, datetime

from extensions import db


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=False,
    )

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )

    item = db.relationship(
        "Item",
        back_populates="conversations",
    )

    buyer = db.relationship(
        "User",
        foreign_keys=[buyer_id],
        back_populates="buyer_conversations",
    )

    seller = db.relationship(
        "User",
        foreign_keys=[seller_id],
        back_populates="seller_conversations",
    )

    messages = db.relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="Message.created_at",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "item_id",
            "buyer_id",
            "seller_id",
            name="uq_conversation_item_buyer_seller",
        ),
        db.CheckConstraint(
            "buyer_id != seller_id",
            name="ck_conversation_different_users",
        ),
    )

    def other_participant(self, user_id):
        if user_id == self.buyer_id:
            return self.seller

        return self.buyer
