import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "studexel-dev-key"

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(BASE_DIR, '../database/studexel.db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False