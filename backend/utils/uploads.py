import os
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


def save_item_image(image_file):

    if not image_file or not image_file.filename:
        return None

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
        exist_ok=True
    )

    image_path = os.path.join(
        upload_folder,
        unique_filename
    )

    image_file.save(
        image_path
    )

    return unique_filename


def delete_item_image(filename):

    if not filename:
        return

    upload_folder = current_app.config[
        "ITEM_IMAGE_UPLOAD_FOLDER"
    ]

    image_path = os.path.join(
        upload_folder,
        filename
    )

    if os.path.isfile(image_path):
        os.remove(image_path)