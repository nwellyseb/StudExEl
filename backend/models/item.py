"""
Item model.

Represents a marketplace listing created by a student.
"""

from datetime import datetime

from extensions import db


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    condition = db.Column(
        db.String(30),
        nullable=False
    )

    image = db.Column(
        db.String(255)
    )

    status = db.Column(
        db.String(20),
        default="Available"
    )

    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    views = db.Column(
        db.Integer,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    school_id = db.Column(
        db.Integer,
        db.ForeignKey("schools.id"),
        nullable=False
    )

    seller = db.relationship(
        "User",
        back_populates="items"
    )

    category = db.relationship(
        "Category",
        back_populates="items"
    )

    school = db.relationship(
        "School",
        back_populates="items"
    )