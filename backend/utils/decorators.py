from functools import wraps

from flask import (
    flash,
    redirect,
    session,
    url_for,
)

from extensions import db
from models.user import User


def login_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        user_id = session.get("user_id")

        if user_id is None:

            flash(
                "Please log in first.",
                "warning",
            )

            return redirect(
                url_for("auth.login")
            )

        user = (
            User.query
            .populate_existing()
            .filter_by(id=user_id)
            .first()
        )

        if user is None:

            session.clear()

            flash(
                "Your session is no longer valid.",
                "warning",
            )

            return redirect(
                url_for("auth.login")
            )

        if not user.is_active:

            session.clear()

            flash(
                "Your account has been suspended. "
                "Please contact an administrator.",
                "danger",
            )

            return redirect(
                url_for("auth.login")
            )

        return view_function(
            *args,
            **kwargs,
        )

    return wrapped_view


def admin_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        user_id = session.get("user_id")

        if user_id is None:

            flash(
                "Please log in first.",
                "warning",
            )

            return redirect(
                url_for("auth.login")
            )

        user = (
            User.query
            .populate_existing()
            .filter_by(id=user_id)
            .first()
        )

        if user is None:

            session.clear()

            flash(
                "Your session is no longer valid.",
                "warning",
            )

            return redirect(
                url_for("auth.login")
            )

        if not user.is_admin:

            flash(
                "Administrator access is required.",
                "danger",
            )

            return redirect(
                url_for("profile.dashboard")
            )

        return view_function(
            *args,
            **kwargs,
        )

    return wrapped_view
