import os


BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

DATABASE_PATH = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "database",
        "studexel.db",
    )
)


class Config:

    SECRET_KEY = "studexel-dev-key"

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{DATABASE_PATH}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ITEM_IMAGE_UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "uploads",
        "items",
    )

    # Maximum upload size: 5 MB.
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024