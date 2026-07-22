import os

from dotenv import load_dotenv


BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
    )
)

ENV_FILE = os.path.join(
    PROJECT_ROOT,
    ".env",
)

load_dotenv(
    ENV_FILE
)


def get_required_environment_variable(name):

    value = os.getenv(name)

    if not value:

        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


def get_boolean_environment_variable(
    name,
    default=False,
):

    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


DATABASE_PATH = os.path.join(
    PROJECT_ROOT,
    "database",
    "studexel.db",
)


def get_database_url():

    database_url = os.getenv(
        "DATABASE_URL"
    )

    if not database_url:

        return (
            f"sqlite:///{DATABASE_PATH}"
        )

    if database_url.startswith(
        "postgres://"
    ):

        return database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    if database_url.startswith(
        "postgresql://"
    ):

        return database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return database_url


def get_item_image_upload_folder():

    return os.getenv(
        "ITEM_IMAGE_UPLOAD_FOLDER"
    ) or os.path.join(
        BASE_DIR,
        "static",
        "uploads",
        "items",
    )


class Config:

    SECRET_KEY = get_required_environment_variable(
        "SECRET_KEY"
    )

    SQLALCHEMY_DATABASE_URI = (
        get_database_url()
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    ITEM_IMAGE_UPLOAD_FOLDER = (
        get_item_image_upload_folder()
    )

    MAX_CONTENT_LENGTH = (
        5 * 1024 * 1024
    )

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = (
        get_boolean_environment_variable(
            "SESSION_COOKIE_SECURE",
            default=False,
        )
    )
