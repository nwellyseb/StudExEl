from flask import current_app
from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)


EMAIL_VERIFICATION_SALT = "studexel-email-verification"
PASSWORD_RESET_SALT = "studexel-password-reset"


def _serializer():

    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )


def generate_email_verification_token(user):

    return _serializer().dumps(
        {
            "user_id": user.id,
            "email": user.email,
        },
        salt=EMAIL_VERIFICATION_SALT,
    )


def load_email_verification_token(token):

    try:
        return _serializer().loads(
            token,
            salt=EMAIL_VERIFICATION_SALT,
            max_age=current_app.config[
                "EMAIL_VERIFICATION_MAX_AGE"
            ],
        )
    except (
        BadSignature,
        SignatureExpired,
    ):
        return None


def generate_password_reset_token(user):

    return _serializer().dumps(
        {
            "user_id": user.id,
            "email": user.email,
            "password_hash": user.password_hash,
        },
        salt=PASSWORD_RESET_SALT,
    )


def load_password_reset_token(token):

    try:
        return _serializer().loads(
            token,
            salt=PASSWORD_RESET_SALT,
            max_age=current_app.config[
                "PASSWORD_RESET_MAX_AGE"
            ],
        )
    except (
        BadSignature,
        SignatureExpired,
    ):
        return None
