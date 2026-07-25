from flask import (
    current_app,
    url_for,
)
from markupsafe import escape

from utils.auth_tokens import (
    generate_email_verification_token,
    generate_password_reset_token,
)
from utils.email_service import send_email


def _absolute_url(endpoint, **values):

    path = url_for(
        endpoint,
        **values,
    )

    return (
        f"{current_app.config['APP_BASE_URL']}"
        f"{path}"
    )


def send_verification_email(user):

    token = generate_email_verification_token(
        user
    )

    verification_url = _absolute_url(
        "auth.verify_email",
        token=token,
    )

    safe_name = escape(
        user.first_name
    )

    return send_email(
        recipient=user.email,
        subject="Verify your StudExEl email",
        html=f"""
            <p>Hello {safe_name},</p>
            <p>
                Verify your email address by clicking
                the link below:
            </p>
            <p>
                <a href="{verification_url}">
                    Verify Email
                </a>
            </p>
            <p>
                This link expires in 24 hours.
            </p>
        """,
        text=(
            f"Hello {user.first_name},\n\n"
            "Verify your StudExEl email address:\n"
            f"{verification_url}\n\n"
            "This link expires in 24 hours."
        ),
    )


def send_password_reset_email(user):

    token = generate_password_reset_token(
        user
    )

    reset_url = _absolute_url(
        "auth.reset_password",
        token=token,
    )

    safe_name = escape(
        user.first_name
    )

    return send_email(
        recipient=user.email,
        subject="Reset your StudExEl password",
        html=f"""
            <p>Hello {safe_name},</p>
            <p>
                Use the link below to reset your
                password:
            </p>
            <p>
                <a href="{reset_url}">
                    Reset Password
                </a>
            </p>
            <p>
                This link expires in one hour.
            </p>
            <p>
                Ignore this email if you did not
                request a password reset.
            </p>
        """,
        text=(
            f"Hello {user.first_name},\n\n"
            "Reset your StudExEl password:\n"
            f"{reset_url}\n\n"
            "This link expires in one hour. "
            "Ignore this email if you did not "
            "request it."
        ),
    )
