from io import BytesIO
from pathlib import Path

from extensions import db
from models.item import Item


def test_user_can_create_listing_with_image(
    logged_in_client,
    app,
    user,
    category,
):

    image_data = BytesIO(
        b"\x89PNG\r\n\x1a\n"
        b"studexel-test-image"
    )

    response = logged_in_client.post(
        "/sell",
        data={
            "title": "Textbook With Image",
            "description": (
                "A textbook listing created "
                "with an uploaded test image."
            ),
            "price": "500.00",
            "condition": "Like New",
            "category": str(category.id),
            "status": "Available",
            "image": (
                image_data,
                "textbook.png",
            ),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Your item has been listed!"
        in response.data
    )

    with app.app_context():

        item = db.session.execute(
            db.select(Item).where(
                Item.title
                == "Textbook With Image"
            )
        ).scalar_one_or_none()

        assert item is not None
        assert item.image is not None
        assert item.image.endswith(".png")
        assert item.seller_id == user.id

        upload_folder = Path(
            app.config[
                "ITEM_IMAGE_UPLOAD_FOLDER"
            ]
        )

        uploaded_file = (
            upload_folder / item.image
        )

        assert uploaded_file.exists()
        assert uploaded_file.is_file()


def test_invalid_image_extension_is_rejected(
    logged_in_client,
    app,
    category,
):

    invalid_file = BytesIO(
        b"this is not an allowed image"
    )

    response = logged_in_client.post(
        "/sell",
        data={
            "title": "Invalid Upload",
            "description": (
                "This listing uses an unsupported "
                "image file extension."
            ),
            "price": "100.00",
            "condition": "Good",
            "category": str(category.id),
            "image": (
                invalid_file,
                "malicious.exe",
            ),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Only JPG, JPEG, PNG, and WEBP "
        b"images are allowed."
        in response.data
    )

    with app.app_context():

        item = db.session.execute(
            db.select(Item).where(
                Item.title
                == "Invalid Upload"
            )
        ).scalar_one_or_none()

        assert item is None


def test_deleting_listing_removes_image_file(
    logged_in_client,
    app,
    category,
):

    image_data = BytesIO(
        b"\x89PNG\r\n\x1a\n"
        b"image-to-be-deleted"
    )

    response = logged_in_client.post(
        "/sell",
        data={
            "title": "Delete Image Test",
            "description": (
                "This listing tests whether its "
                "image is deleted correctly."
            ),
            "price": "250.00",
            "condition": "Good",
            "category": str(category.id),
            "image": (
                image_data,
                "delete-test.png",
            ),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():

        item = db.session.execute(
            db.select(Item).where(
                Item.title
                == "Delete Image Test"
            )
        ).scalar_one()

        item_id = item.id

        uploaded_file = Path(
            app.config[
                "ITEM_IMAGE_UPLOAD_FOLDER"
            ]
        ) / item.image

        assert uploaded_file.exists()

    response = logged_in_client.post(
        f"/delete/{item_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Listing deleted successfully!"
        in response.data
    )

    with app.app_context():

        deleted_item = db.session.get(
            Item,
            item_id,
        )

        assert deleted_item is None

    assert not uploaded_file.exists()


def test_replacing_image_removes_old_file(
    logged_in_client,
    app,
    category,
):

    first_image = BytesIO(
        b"\x89PNG\r\n\x1a\n"
        b"original-image"
    )

    response = logged_in_client.post(
        "/sell",
        data={
            "title": "Replace Image Test",
            "description": (
                "This listing tests whether an old "
                "image is removed after replacement."
            ),
            "price": "300.00",
            "condition": "Good",
            "category": str(category.id),
            "image": (
                first_image,
                "original-image.png",
            ),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():

        item = db.session.execute(
            db.select(Item).where(
                Item.title
                == "Replace Image Test"
            )
        ).scalar_one()

        item_id = item.id
        old_filename = item.image

        upload_folder = Path(
            app.config[
                "ITEM_IMAGE_UPLOAD_FOLDER"
            ]
        )

        old_file = (
            upload_folder / old_filename
        )

        assert old_file.exists()

    replacement_image = BytesIO(
        b"\x89PNG\r\n\x1a\n"
        b"replacement-image"
    )

    response = logged_in_client.post(
        f"/edit/{item_id}",
        data={
            "title": "Replace Image Test",
            "description": (
                "This listing now contains "
                "a replacement image."
            ),
            "price": "350.00",
            "condition": "Like New",
            "category": str(category.id),
            "status": "Available",
            "image": (
                replacement_image,
                "replacement-image.png",
            ),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Listing updated successfully!"
        in response.data
    )

    with app.app_context():

        updated_item = db.session.get(
            Item,
            item_id,
        )

        assert updated_item is not None
        assert updated_item.image is not None

        assert (
            updated_item.image
            != old_filename
        )

        new_file = (
            upload_folder
            / updated_item.image
        )

        assert new_file.exists()
        assert new_file.is_file()

    assert not old_file.exists()
