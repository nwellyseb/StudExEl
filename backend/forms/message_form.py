from flask_wtf import FlaskForm

from wtforms import (
    SubmitField,
    TextAreaField,
)

from wtforms.validators import (
    DataRequired,
    Length,
)


class MessageForm(FlaskForm):

    body = TextAreaField(
        "Message",
        validators=[
            DataRequired(
                message="Enter a message before sending."
            ),
            Length(
                max=2000,
                message=(
                    "Messages cannot exceed "
                    "2,000 characters."
                ),
            ),
        ],
    )

    submit = SubmitField(
        "Send Message"
    )
