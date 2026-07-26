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

from forms.login_form import LoginForm
from forms.password_reset_form import (
    PasswordResetForm,
    PasswordResetRequestForm,
)
from forms.registration_form import RegistrationForm

from models.school import School
from models.user import User

from utils.auth_emails import (
    send_password_reset_email,
    send_verification_email,
)
from utils.auth_tokens import (
    load_email_verification_token,
    load_password_reset_token,
)


auth = Blueprint(
    "auth",
    __name__,
)


@auth.route(
    "/register",
    methods=["GET", "POST"],
)
def register():

    form = RegistrationForm()

    if form.validate_on_submit():

        try:
            school_id = int(
                form.school.data
            )
        except (TypeError, ValueError):
            flash(
                "Please select a valid school.",
                "danger",
            )

            return render_template(
                "register.html",
                form=form,
            )

        selected_school = db.session.get(
            School,
            school_id,
        )

        if (
            selected_school is None
            or not selected_school.is_active
        ):
            flash(
                "Please select a valid school.",
                "danger",
            )

            return render_template(
                "register.html",
                form=form,
            )

        existing_username = User.query.filter_by(
            username=form.username.data
        ).first()

        if existing_username:

            flash(
                "Username already exists.",
                "danger",
            )

            return render_template(
                "register.html",
                form=form,
            )

        normalized_email = (
            form.email.data.strip().lower()
        )

        existing_email = User.query.filter(
            db.func.lower(User.email)
            == normalized_email
        ).first()

        if existing_email:

            flash(
                "Email already exists.",
                "danger",
            )

            return render_template(
                "register.html",
                form=form,
            )

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=normalized_email,
            school_id=selected_school.id,
        )

        user.set_password(
            form.password.data
        )

        db.session.add(user)
        db.session.commit()

        try:
            send_verification_email(
                user
            )
        except Exception:
            current_app.logger.exception(
                "Failed to send registration verification email "
                "for user_id=%s",
                user.id,
            )

            flash(
                "Your account was created, but the "
                "verification email could not be sent. "
                "Please try again later.",
                "warning",
            )
        else:
            flash(
                "Account created. Check your email "
                "to verify your address before logging in.",
                "success",
            )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html",
        form=form,
    )


@auth.route(
    "/verify-email/<token>",
)
def verify_email(token):

    data = load_email_verification_token(
        token
    )

    if data is None:

        flash(
            "That verification link is invalid or has expired.",
            "danger",
        )

        return redirect(
            url_for("auth.login")
        )

    user = db.session.get(
        User,
        data.get("user_id"),
    )

    if (
        user is None
        or user.email != data.get("email")
    ):

        flash(
            "That verification link is no longer valid.",
            "danger",
        )

        return redirect(
            url_for("auth.login")
        )

    if user.email_verified_at is None:

        user.email_verified_at = (
            datetime.now(UTC)
            .replace(tzinfo=None)
        )

        db.session.commit()

    flash(
        "Your email has been verified. You may now log in.",
        "success",
    )

    return redirect(
        url_for("auth.login")
    )


@auth.route(
    "/login",
    methods=["GET", "POST"],
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

            if not user.is_active:

                session.clear()

                flash(
                    "Your account has been suspended. "
                    "Please contact an administrator.",
                    "danger",
                )

                return render_template(
                    "login.html",
                    form=form,
                )

            if (
                not user.is_admin
                and user.email_verified_at is None
            ):

                flash(
                    "Verify your email before logging in.",
                    "warning",
                )

                return render_template(
                    "login.html",
                    form=form,
                )

            session["user_id"] = user.id

            flash(
                f"Welcome back, {user.first_name}!",
                "success",
            )

            return redirect(
                url_for("profile.dashboard")
            )

        flash(
            "Invalid username or password.",
            "danger",
        )

    return render_template(
        "login.html",
        form=form,
    )


@auth.route(
    "/forgot-password",
    methods=["GET", "POST"],
)
def forgot_password():

    form = PasswordResetRequestForm()

    if form.validate_on_submit():

        normalized_email = (
            form.email.data.strip().lower()
        )

        user = User.query.filter(
            db.func.lower(User.email)
            == normalized_email
        ).first()

        if (
            user is not None
            and user.email_verified_at is not None
            and user.is_active
        ):

            try:
                send_password_reset_email(
                    user
                )
            except Exception:
                pass

        flash(
            "If an eligible account exists for that "
            "email, a password-reset link has been sent.",
            "info",
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "forgot_password.html",
        form=form,
    )


@auth.route(
    "/reset-password/<token>",
    methods=["GET", "POST"],
)
def reset_password(token):

    data = load_password_reset_token(
        token
    )

    user = None

    if data is not None:

        user = db.session.get(
            User,
            data.get("user_id"),
        )

    if (
        user is None
        or user.email != data.get("email")
        or user.password_hash
        != data.get("password_hash")
        or user.email_verified_at is None
        or not user.is_active
    ):

        flash(
            "That password-reset link is invalid or has expired.",
            "danger",
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    form = PasswordResetForm()

    if form.validate_on_submit():

        user.set_password(
            form.password.data
        )

        db.session.commit()
        session.clear()

        flash(
            "Your password has been reset. "
            "You may now log in.",
            "success",
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "reset_password.html",
        form=form,
    )


@auth.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(
        url_for("auth.login")
    )
