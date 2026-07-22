"""
User model.

Represents every student or administrator registered in StudExEl.
Each user belongs to one school.
"""

from datetime import UTC, datetime

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    first_name = db.Column(
        db.String(100),
        nullable=False,
    )

    last_name = db.Column(
        db.String(100),
        nullable=False,
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    profile_photo = db.Column(
        db.String(255),
    )

    bio = db.Column(
        db.Text,
    )

    course = db.Column(
        db.String(100),
    )

    year_level = db.Column(
        db.String(30),
    )

    verification_status = db.Column(
        db.String(20),
        default="Pending",
    )

    is_admin = db.Column(
        db.Boolean,
        default=False,
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
    )

    school_id = db.Column(
        db.Integer,
        db.ForeignKey("schools.id"),
        nullable=False,
    )

    school = db.relationship(
        "School",
        back_populates="users",
    )

    items = db.relationship(
        "Item",
        back_populates="seller",
        cascade="all, delete-orphan",
        lazy=True,
    )

    buyer_conversations = db.relationship(
        "Conversation",
        foreign_keys="Conversation.buyer_id",
        back_populates="buyer",
        cascade="all, delete-orphan",
        lazy=True,
    )

    seller_conversations = db.relationship(
        "Conversation",
        foreign_keys="Conversation.seller_id",
        back_populates="seller",
        cascade="all, delete-orphan",
        lazy=True,
    )

    sent_messages = db.relationship(
        "Message",
        back_populates="sender",
        cascade="all, delete-orphan",
        lazy=True,
    )

    submitted_reports = db.relationship(
        "Report",
        foreign_keys="Report.reporter_id",
        back_populates="reporter",
        cascade="all, delete-orphan",
        lazy=True,
    )

    received_reports = db.relationship(
        "Report",
        foreign_keys="Report.reported_user_id",
        back_populates="reported_user",
        lazy=True,
    )

    reviewed_reports = db.relationship(
        "Report",
        foreign_keys="Report.reviewed_by_id",
        back_populates="reviewed_by",
        lazy=True,
    )

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password,
            method="pbkdf2:sha256",
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password,
        )

    @property
    def full_name(self):

        return (
            f"{self.first_name} "
            f"{self.last_name}"
        )