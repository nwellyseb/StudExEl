import os


# Config requires a secret when imported. Tests must not depend
# on a developer having a local .env file.
os.environ.setdefault(
    "SECRET_KEY",
    "studexel-test-key",
)


from config import (
    DATABASE_PATH,
    get_database_url,
    get_item_image_upload_folder,
)


def test_database_url_defaults_to_sqlite(
    monkeypatch,
):

    monkeypatch.delenv(
        "DATABASE_URL",
        raising=False,
    )

    assert get_database_url() == (
        f"sqlite:///{DATABASE_PATH}"
    )


def test_database_url_converts_postgres_scheme(
    monkeypatch,
):

    monkeypatch.setenv(
        "DATABASE_URL",
        (
            "postgres://student:password"
            "@database.example/studexel"
        ),
    )

    assert get_database_url() == (
        "postgresql+psycopg://"
        "student:password"
        "@database.example/studexel"
    )


def test_database_url_converts_postgresql_scheme(
    monkeypatch,
):

    monkeypatch.setenv(
        "DATABASE_URL",
        (
            "postgresql://student:password"
            "@database.example/studexel"
        ),
    )

    assert get_database_url() == (
        "postgresql+psycopg://"
        "student:password"
        "@database.example/studexel"
    )


def test_database_url_preserves_psycopg_scheme(
    monkeypatch,
):

    expected_url = (
        "postgresql+psycopg://"
        "student:password"
        "@database.example/studexel"
    )

    monkeypatch.setenv(
        "DATABASE_URL",
        expected_url,
    )

    assert get_database_url() == expected_url


def test_upload_folder_can_be_overridden(
    monkeypatch,
    tmp_path,
):

    upload_folder = (
        tmp_path / "item-uploads"
    )

    monkeypatch.setenv(
        "ITEM_IMAGE_UPLOAD_FOLDER",
        str(upload_folder),
    )

    assert (
        get_item_image_upload_folder()
        == str(upload_folder)
    )
