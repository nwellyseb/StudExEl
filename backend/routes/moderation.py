"""
Administrator moderation routes.
"""

from datetime import UTC, datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from extensions import db
from models.report import Report
from models.user import User
from utils.decorators import admin_required


moderation = Blueprint(
    "moderation",
    __name__,
    url_prefix="/admin",
)


REPORT_STATUSES = [
    "Pending",
    "Reviewed",
    "Dismissed",
    "Actioned",
]


def mark_report_actioned(report):
    """Record that an administrator took action on a report."""

    report.status = "Actioned"
    report.reviewed_by_id = session["user_id"]
    report.reviewed_at = datetime.now(UTC).replace(tzinfo=None)


def get_report_target_user(report):
    """Return a freshly loaded report target user."""

    target_user_id = report.reported_user_id

    if (
        target_user_id is None
        and report.reported_item is not None
    ):
        target_user_id = report.reported_item.seller_id

    if target_user_id is None:
        return None

    return (
        User.query
        .populate_existing()
        .filter_by(id=target_user_id)
        .first()
    )


@moderation.route("/reports")
@admin_required
def report_list():

    status_filter = request.args.get(
        "status",
        "Pending",
    ).strip()

    query = Report.query

    if status_filter in REPORT_STATUSES:

        query = query.filter_by(
            status=status_filter,
        )

    elif status_filter != "All":

        status_filter = "Pending"

        query = query.filter_by(
            status="Pending",
        )

    reports = query.order_by(
        Report.created_at.desc()
    ).all()

    return render_template(
        "moderation/reports.html",
        reports=reports,
        statuses=REPORT_STATUSES,
        selected_status=status_filter,
    )


@moderation.route(
    "/reports/<int:report_id>/status",
    methods=["POST"],
)
@admin_required
def update_report_status(report_id):

    report = db.get_or_404(
        Report,
        report_id,
    )

    new_status = request.form.get(
        "status",
        "",
    ).strip()

    if new_status not in REPORT_STATUSES:

        flash(
            "Invalid report status.",
            "danger",
        )

        return redirect(
            url_for("moderation.report_list")
        )

    report.status = new_status
    report.reviewed_by_id = session["user_id"]
    report.reviewed_at = datetime.now(UTC).replace(tzinfo=None)

    db.session.commit()

    flash(
        "Report status updated successfully.",
        "success",
    )

    return redirect(
        url_for("moderation.report_list")
    )


@moderation.route(
    "/reports/<int:report_id>/remove-listing",
    methods=["POST"],
)
@admin_required
def remove_reported_listing(report_id):

    report = db.get_or_404(
        Report,
        report_id,
    )

    item = report.reported_item

    if item is None:

        flash(
            "This report is not connected to a listing.",
            "danger",
        )

        return redirect(
            url_for("moderation.report_list")
        )

    if item.status == "Removed":

        flash(
            "This listing has already been removed.",
            "info",
        )

        return redirect(
            url_for("moderation.report_list")
        )

    item.status = "Removed"
    mark_report_actioned(report)

    db.session.commit()

    flash(
        "Listing removed successfully.",
        "success",
    )

    return redirect(
        url_for("moderation.report_list")
    )


@moderation.route(
    "/reports/<int:report_id>/suspend-user",
    methods=["POST"],
)
@admin_required
def suspend_reported_user(report_id):

    report = db.get_or_404(
        Report,
        report_id,
    )

    user = get_report_target_user(report)

    if user is None:

        flash(
            "This report is not connected to a user.",
            "danger",
        )

        return redirect(
            url_for("moderation.report_list")
        )

    if user.id == session["user_id"]:

        flash(
            "You cannot suspend your own account.",
            "danger",
        )

        return redirect(
            url_for("moderation.report_list")
        )

    if user.is_admin:

        flash(
            "Administrator accounts cannot be suspended here.",
            "danger",
        )

        return redirect(
            url_for("moderation.report_list")
        )

    if not user.is_active:

        flash(
            "This user is already suspended.",
            "info",
        )

        return redirect(
            url_for("moderation.report_list")
        )

    user.is_active = False
    mark_report_actioned(report)

    db.session.commit()

    flash(
        "User suspended successfully.",
        "success",
    )

    return redirect(
        url_for("moderation.report_list")
    )


@moderation.route(
    "/users/<int:user_id>/reactivate",
    methods=["POST"],
)
@admin_required
def reactivate_user(user_id):

    user = (
        User.query
        .populate_existing()
        .filter_by(id=user_id)
        .first_or_404()
    )

    if user.is_active:

        flash(
            "This user is already active.",
            "info",
        )

        return redirect(
            url_for("moderation.report_list")
        )

    user.is_active = True

    db.session.commit()

    flash(
        "User reactivated successfully.",
        "success",
    )

    return redirect(
        url_for("moderation.report_list")
    )
