import os
from uuid import uuid4

import cloudinary.uploader
from cloudinary import CloudinaryImage
from flask import current_app, url_for
from werkzeug.utils import secure_filename


CLOUDINARY_IMAGE_PREFIX = "cloudinary:"
CLOUDINARY_ITEM_FOLDER = "studexel/items"
CLOUDINARY_VERIFICATION_FOLDER = (
    "studexel/verifications"
)


def is_cloudinary_image(filename):

    return bool(
        filename
        and filename.startswith(
            CLOUDINARY_IMAGE_PREFIX
        )
    )


def get_cloudinary_public_id(filename):

    return filename.removeprefix(
        CLOUDINARY_IMAGE_PREFIX
    )


def save_item_image(image_file):

    if not image_file or not image_file.filename:
        return None

    storage_backend = current_app.config.get(
        "ITEM_IMAGE_STORAGE",
        "local",
    )

    if storage_backend == "cloudinary":

        image_source = getattr(
            image_file,
            "stream",
            image_file,
        )

        if hasattr(
            image_source,
            "seek",
        ):
            image_source.seek(0)

        requested_public_id = (
            f"{CLOUDINARY_ITEM_FOLDER}/"
            f"{uuid4().hex}"
        )

        upload_result = (
            cloudinary.uploader.upload(
                image_source,
                public_id=requested_public_id,
                resource_type="image",
                overwrite=False,
            )
        )

        public_id = upload_result.get(
            "public_id"
        )

        if not public_id:

            raise RuntimeError(
                "Cloudinary upload did not "
                "return a public ID."
            )

        return (
            f"{CLOUDINARY_IMAGE_PREFIX}"
            f"{public_id}"
        )

    if storage_backend != "local":

        raise RuntimeError(
            "Unsupported item image storage "
            f"backend: {storage_backend}"
        )

    safe_filename = secure_filename(
        image_file.filename
    )

    _, file_extension = os.path.splitext(
        safe_filename
    )

    unique_filename = (
        f"{uuid4().hex}"
        f"{file_extension.lower()}"
    )

    upload_folder = current_app.config[
        "ITEM_IMAGE_UPLOAD_FOLDER"
    ]

    os.makedirs(
        upload_folder,
        exist_ok=True,
    )

    image_path = os.path.join(
        upload_folder,
        unique_filename,
    )

    image_file.save(
        image_path
    )

    return unique_filename


def delete_item_image(filename):

    if not filename:
        return

    if is_cloudinary_image(
        filename
    ):

        public_id = get_cloudinary_public_id(
            filename
        )

        cloudinary.uploader.destroy(
            public_id,
            resource_type="image",
            invalidate=True,
        )

        return

    upload_folder = current_app.config[
        "ITEM_IMAGE_UPLOAD_FOLDER"
    ]

    image_path = os.path.join(
        upload_folder,
        filename,
    )

    if os.path.isfile(image_path):
        os.remove(image_path)


def get_item_image_url(filename):

    if not filename:
        return None

    if is_cloudinary_image(
        filename
    ):

        public_id = get_cloudinary_public_id(
            filename
        )

        return CloudinaryImage(
            public_id
        ).build_url(
            secure=True
        )

    return url_for(
        "static",
        filename=(
            f"uploads/items/{filename}"
        ),
    )



def save_verification_document(document_file):

    if (
        not document_file
        or not document_file.filename
    ):
        raise ValueError(
            "A verification document is required."
        )

    document_source = getattr(
        document_file,
        "stream",
        document_file,
    )

    if hasattr(
        document_source,
        "seek",
    ):
        document_source.seek(0)

    requested_public_id = (
        f"{CLOUDINARY_VERIFICATION_FOLDER}/"
        f"{uuid4().hex}"
    )

    upload_result = cloudinary.uploader.upload(
        document_source,
        public_id=requested_public_id,
        resource_type="image",
        type="authenticated",
        allowed_formats=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],
        overwrite=False,
    )

    public_id = upload_result.get(
        "public_id"
    )

    document_format = upload_result.get(
        "format"
    )

    if not public_id or not document_format:
        raise RuntimeError(
            "Cloudinary did not return the "
            "verification document details."
        )

    return {
        "public_id": public_id,
        "format": document_format,
    }


def delete_verification_document(
    public_id,
):

    if not public_id:
        return

    cloudinary.uploader.destroy(
        public_id,
        resource_type="image",
        type="authenticated",
        invalidate=True,
    )



def get_verification_document_url(
    public_id,
    document_format,
):

    if not public_id or not document_format:
        return None

    return CloudinaryImage(
        public_id
    ).build_url(
        type="authenticated",
        format=document_format,
        sign_url=True,
        secure=True,
    )
