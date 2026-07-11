from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
)


class EditProfileForm(FlaskForm):

    course = StringField(
        "Course",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    year_level = StringField(
        "Year Level",
        validators=[
            Optional(),
            Length(max=30)
        ]
    )

    bio = TextAreaField(
        "About Me",
        validators=[
            Optional(),
            Length(max=500)
        ]
    )

    submit = SubmitField(
        "Save Changes"
    )