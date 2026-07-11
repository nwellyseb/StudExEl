from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    session,
    url_for,
)

from extensions import db

from forms.edit_profile_form import EditProfileForm
from models.user import User

from utils.decorators import login_required


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