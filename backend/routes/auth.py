from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)

from extensions import db

from forms.registration_form import RegistrationForm
from forms.login_form import LoginForm

from models.user import User
from models.school import School


auth = Blueprint(
    "auth",
    __name__
)


@auth.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    form = RegistrationForm()

    schools = School.query.order_by(
        School.school_name
    ).all()

    form.school.choices = [
        (
            school.id,
            school.school_name
        )
        for school in schools
    ]

    if form.validate_on_submit():

        existing_username = User.query.filter_by(
            username=form.username.data
        ).first()

        if existing_username:

            flash(
                "Username already exists.",
                "danger"
            )

            return render_template(
                "register.html",
                form=form
            )

        existing_email = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_email:

            flash(
                "Email already exists.",
                "danger"
            )

            return render_template(
                "register.html",
                form=form
            )

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            school_id=form.school.data,
        )

        user.set_password(
            form.password.data
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Account created successfully! Please log in.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html",
        form=form
    )


@auth.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            username=form.username.data
        ).first()

        if user and user.check_password(
            form.password.data
        ):

            session["user_id"] = user.id

            flash(
                f"Welcome back, {user.first_name}!",
                "success"
            )

            return redirect(
                url_for("profile.dashboard")
            )

        flash(
            "Invalid username or password.",
            "danger"
        )

    return render_template(
        "login.html",
        form=form
    )


@auth.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )