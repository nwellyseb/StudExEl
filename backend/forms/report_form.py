"""
Forms used to submit marketplace reports.
"""

from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Length,
)


class ReportForm(FlaskForm):

    reason = SelectField(
        "Reason",
        choices=[
            (
                "",
                "Select a reason",
            ),
            (
                "Scam or fraud",
                "Scam or fraud",
            ),
            (
                "Misleading information",
                "Misleading information",
            ),
            (
                "Harassment or abusive behavior",
                "Harassment or abusive behavior",
            ),
            (
                "Spam or duplicate content",
                "Spam or duplicate content",
            ),
            (
                "Prohibited or inappropriate content",
                "Prohibited or inappropriate content",
            ),
            (
                "Other",
                "Other",
            ),
        ],
        validators=[
            DataRequired(
                message="Please select a report reason."
            ),
        ],
    )

    details = TextAreaField(
        "Details",
        validators=[
            DataRequired(
                message="Please explain the reason for your report."
            ),
            Length(
                min=10,
                max=1000,
                message=(
                    "Report details must be between "
                    "10 and 1000 characters."
                ),
            ),
        ],
    )

    submit = SubmitField(
        "Submit Report",
    )
