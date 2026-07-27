from flask_wtf import FlaskForm
from flask_wtf.file import (
    FileAllowed,
    FileField,
    FileRequired,
)
from wtforms import SubmitField


class StudentVerificationForm(FlaskForm):

    document = FileField(
        "Student ID or Enrollment Proof",
        validators=[
            FileRequired(
                "Select a verification image."
            ),
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                (
                    "Only JPG, JPEG, PNG, and WEBP "
                    "images are allowed."
                ),
            ),
        ],
    )

    submit = SubmitField(
        "Submit for Verification"
    )
