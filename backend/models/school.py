"""
School model.

Stores all educational institutions supported by StudExEl.
Every registered user belongs to one school.
"""

from extensions import db


class School(db.Model):
    __tablename__ = "schools"

    __table_args__ = (
        db.UniqueConstraint(
            "directory_source",
            "official_school_code",
            "school_name",
            name="uq_schools_source_code_name",
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    school_name = db.Column(
        db.String(200),
        nullable=False
    )

    short_name = db.Column(
        db.String(50)
    )

    official_school_code = db.Column(
        db.String(50)
    )

    directory_source = db.Column(
        db.String(20)
    )

    school_type = db.Column(
        db.String(50)
    )

    sector = db.Column(
        db.String(20)
    )

    region = db.Column(
        db.String(100)
    )

    province = db.Column(
        db.String(100)
    )

    city = db.Column(
        db.String(100)
    )

    website = db.Column(
        db.String(255)
    )

    latitude = db.Column(
        db.Float
    )

    longitude = db.Column(
        db.Float
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    users = db.relationship(
        "User",
        back_populates="school",
        lazy=True
    )

    items = db.relationship(
        "Item",
        back_populates="school",
        cascade="all, delete-orphan",
        lazy=True
    )