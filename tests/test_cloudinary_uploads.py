from io import BytesIO
from unittest.mock import patch

from werkzeug.datastructures import FileStorage

from utils.uploads import (
    delete_item_image,
    get_item_image_url,
    save_item_image,
)


def test_cloudinary_upload_returns_storage_key(
    app,
):

    image_file = FileStorage(
        stream=BytesIO(
            b"cloudinary-test-image"
        ),
        filename="listing.png",
        content_type="image/png",
    )

    with app.app_context():

        app.config[
            "ITEM_IMAGE_STORAGE"
        ] = "cloudinary"

        with patch(
            "utils.uploads."
            "cloudinary.uploader.upload"
        ) as upload:

            upload.return_value = {
                "public_id": (
                    "studexel/items/"
                    "uploaded-image"
                ),
            }

            stored_value = save_item_image(
                image_file
            )

    assert stored_value == (
        "cloudinary:"
        "studexel/items/uploaded-image"
    )

    upload.assert_called_once()

    call_arguments = upload.call_args

    assert (
        call_arguments.kwargs[
            "resource_type"
        ]
        == "image"
    )

    assert (
        call_arguments.kwargs[
            "overwrite"
        ]
        is False
    )

    assert call_arguments.kwargs[
        "public_id"
    ].startswith(
        "studexel/items/"
    )


def test_cloudinary_image_can_be_deleted(
    app,
):

    stored_value = (
        "cloudinary:"
        "studexel/items/deleted-image"
    )

    with app.app_context():

        with patch(
            "utils.uploads."
            "cloudinary.uploader.destroy"
        ) as destroy:

            delete_item_image(
                stored_value
            )

    destroy.assert_called_once_with(
        "studexel/items/deleted-image",
        resource_type="image",
        invalidate=True,
    )


def test_cloudinary_image_url_is_generated(
    app,
):

    expected_url = (
        "https://res.cloudinary.com/"
        "example/image/upload/"
        "studexel/items/listing-image"
    )

    with app.test_request_context():

        with patch(
            "utils.uploads.CloudinaryImage"
        ) as cloudinary_image:

            cloudinary_image.return_value\
                .build_url.return_value = (
                    expected_url
                )

            result = get_item_image_url(
                "cloudinary:"
                "studexel/items/listing-image"
            )

    assert result == expected_url

    cloudinary_image.assert_called_once_with(
        "studexel/items/listing-image"
    )

    cloudinary_image.return_value\
        .build_url.assert_called_once_with(
            secure=True
        )


def test_local_image_url_is_preserved(
    app,
):

    with app.test_request_context():

        result = get_item_image_url(
            "local-image.png"
        )

    assert result == (
        "/static/uploads/items/"
        "local-image.png"
    )
