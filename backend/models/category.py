from extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    category_name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    slug = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    description = db.Column(
        db.Text
    )

    icon = db.Column(
        db.String(100)
    )

    display_order = db.Column(
        db.Integer,
        default=0
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    items = db.relationship(
        "Item",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy=True
    )