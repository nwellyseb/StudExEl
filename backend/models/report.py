"""
Report model.

Stores reports submitted against marketplace listings or users.
"""

from datetime import UTC, datetime

from extensions import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    reporter_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    reported_item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=True,
    )

    reported_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    reason = db.Column(
        db.String(50),
        nullable=False,
    )

    details = db.Column(
        db.Text,
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        default="Pending",
        nullable=False,
    )

    reviewed_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    reviewed_at = db.Column(
        db.DateTime,
        nullable=True,
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

    reporter = db.relationship(
        "User",
        foreign_keys=[reporter_id],
        back_populates="submitted_reports",
    )

    reported_user = db.relationship(
        "User",
        foreign_keys=[reported_user_id],
        back_populates="received_reports",
    )

    reviewed_by = db.relationship(
        "User",
        foreign_keys=[reviewed_by_id],
        back_populates="reviewed_reports",
    )

    reported_item = db.relationship(
        "Item",
        back_populates="reports",
    )

    __table_args__ = (
        db.CheckConstraint(
            """
            (
                reported_item_id IS NOT NULL
                AND reported_user_id IS NULL
            )
            OR
            (
                reported_item_id IS NULL
                AND reported_user_id IS NOT NULL
            )
            """,
            name="ck_report_exactly_one_target",
        ),
        db.CheckConstraint(
            """
            reported_user_id IS NULL
            OR reporter_id != reported_user_id
            """,
            name="ck_report_cannot_report_self",
        ),
        db.Index(
            "ix_reports_status_created_at",
            "status",
            "created_at",
        ),
    )

    @property
    def target_type(self):

        if self.reported_item_id is not None:
            return "Listing"

        return "User"
