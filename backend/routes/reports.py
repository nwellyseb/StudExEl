"""
Routes for submitting marketplace reports.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    session,
    url_for,
)

from extensions import db
from forms.report_form import ReportForm
from models.item import Item
from models.report import Report
from models.user import User
from utils.decorators import login_required


reports = Blueprint(
    "reports",
    __name__,
)


@reports.route(
    "/reports/item/<int:item_id>",
    methods=["GET", "POST"],
)
@login_required
def report_item(item_id):

    item = db.get_or_404(
        Item,
        item_id,
    )

    current_user_id = session["user_id"]

    if item.seller_id == current_user_id:

        flash(
            "You cannot report your own listing.",
            "warning",
        )

        return redirect(
            url_for(
                "marketplace.item_details",
                item_id=item.id,
            )
        )

    existing_report = Report.query.filter_by(
        reporter_id=current_user_id,
        reported_item_id=item.id,
        status="Pending",
    ).first()

    if existing_report:

        flash(
            "You already have a pending report for this listing.",
            "info",
        )

        return redirect(
            url_for(
                "marketplace.item_details",
                item_id=item.id,
            )
        )

    form = ReportForm()

    if form.validate_on_submit():

        report = Report(
            reporter_id=current_user_id,
            reported_item_id=item.id,
            reason=form.reason.data,
            details=form.details.data.strip(),
            status="Pending",
        )

        db.session.add(report)
        db.session.commit()

        flash(
            "Listing report submitted successfully.",
            "success",
        )

        return redirect(
            url_for(
                "marketplace.item_details",
                item_id=item.id,
            )
        )

    return render_template(
        "reports/submit_report.html",
        form=form,
        target_type="Listing",
        target_name=item.title,
        cancel_url=url_for(
            "marketplace.item_details",
            item_id=item.id,
        ),
    )


@reports.route(
    "/reports/user/<int:user_id>",
    methods=["GET", "POST"],
)
@login_required
def report_user(user_id):

    reported_user = db.get_or_404(
        User,
        user_id,
    )

    current_user_id = session["user_id"]

    if reported_user.id == current_user_id:

        flash(
            "You cannot report yourself.",
            "warning",
        )

        return redirect(
            url_for("marketplace.marketplace_home")
        )

    existing_report = Report.query.filter_by(
        reporter_id=current_user_id,
        reported_user_id=reported_user.id,
        status="Pending",
    ).first()

    if existing_report:

        flash(
            "You already have a pending report for this user.",
            "info",
        )

        return redirect(
            url_for("marketplace.marketplace_home")
        )

    form = ReportForm()

    if form.validate_on_submit():

        report = Report(
            reporter_id=current_user_id,
            reported_user_id=reported_user.id,
            reason=form.reason.data,
            details=form.details.data.strip(),
            status="Pending",
        )

        db.session.add(report)
        db.session.commit()

        flash(
            "User report submitted successfully.",
            "success",
        )

        return redirect(
            url_for("marketplace.marketplace_home")
        )

    return render_template(
        "reports/submit_report.html",
        form=form,
        target_type="User",
        target_name=reported_user.full_name,
        cancel_url=url_for("marketplace.marketplace_home"),
    )
