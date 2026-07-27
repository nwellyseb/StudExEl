from datetime import UTC, datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    session,
    url_for,
)

from extensions import db

from forms.edit_profile_form import EditProfileForm
from forms.student_verification_form import (
    StudentVerificationForm,
)
from models.user import User

from utils.decorators import login_required
from utils.uploads import (
    delete_verification_document,
    save_verification_document,
)


profile = Blueprint(
    "profile",
    __name__,
)


@profile.route("/dashboard")
@login_required
def dashboard():

    user = db.get_or_404(
        User,
        session["user_id"],
    )

    return render_template(
        "dashboard.html",
        user=user,
    )


@profile.route("/profile")
@login_required
def view_profile():

    user = db.get_or_404(
        User,
        session["user_id"],
    )

    return render_template(
        "profile.html",
        user=user,
    )


@profile.route(
    "/profile/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_profile():

    user = db.get_or_404(
        User,
        session["user_id"],
    )

    form = EditProfileForm(
        obj=user,
    )

    if form.validate_on_submit():

        user.course = form.course.data
        user.year_level = form.year_level.data
        user.bio = form.bio.data

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success",
        )

        return redirect(
            url_for("profile.view_profile")
        )

    return render_template(
        "edit_profile.html",
        form=form,
    )


@profile.route(
    "/verification/submit",
    methods=["GET", "POST"],
)
@login_required
def submit_verification():

    user = db.get_or_404(
        User,
        session["user_id"],
    )

    if user.is_admin:

        flash(
            "Administrator accounts do not require "
            "student verification.",
            "info",
        )

        return redirect(
            url_for("profile.dashboard")
        )

    if user.verification_status == "Verified":

        flash(
            "Your student account is already verified.",
            "info",
        )

        return redirect(
            url_for("profile.dashboard")
        )

    form = StudentVerificationForm()

    if form.validate_on_submit():

        previous_public_id = (
            user.verification_document_public_id
        )

        document_data = save_verification_document(
            form.document.data
        )

        user.verification_document_public_id = (
            document_data["public_id"]
        )

        user.verification_document_format = (
            document_data["format"]
        )

        user.verification_status = "Pending"

        user.verification_rejection_reason = None

        user.verification_submitted_at = (
            datetime.now(UTC).replace(tzinfo=None)
        )

        user.verification_reviewed_at = None
        user.verification_reviewed_by_id = None

        db.session.commit()

        if (
            previous_public_id
            and previous_public_id
            != document_data["public_id"]
        ):

            try:
                delete_verification_document(
                    previous_public_id
                )

            except Exception:

                current_app.logger.exception(
                    "Failed to delete replaced "
                    "verification document for user_id=%s",
                    user.id,
                )

        flash(
            "Student verification submitted successfully. "
            "An administrator will review it.",
            "success",
        )

        return redirect(
            url_for("profile.dashboard")
        )

    return render_template(
        "student_verification.html",
        form=form,
        user=user,
    )
