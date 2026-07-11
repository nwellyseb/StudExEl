from flask_wtf import FlaskForm
from flask_wtf.file import (
    FileAllowed,
    FileField,
)

from wtforms import (
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)

from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
)


class ItemForm(FlaskForm):

    title = StringField(
        "Item Name",
        validators=[
            DataRequired(),
            Length(max=150),
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(),
            Length(min=10, max=1000),
        ]
    )

    price = DecimalField(
        "Price (₱)",
        places=2,
        validators=[
            DataRequired(),
            NumberRange(min=0),
        ]
    )

    condition = SelectField(
        "Condition",
        choices=[
            ("Brand New", "Brand New"),
            ("Like New", "Like New"),
            ("Good", "Good"),
            ("Fair", "Fair"),
            ("Used", "Used"),
        ],
        validators=[
            DataRequired(),
        ]
    )

    category = SelectField(
        "Category",
        coerce=int,
        validators=[
            DataRequired(),
        ]
    )

    image = FileField(
        "Item Image",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Only JPG, JPEG, PNG, and WEBP images are allowed.",
            ),
        ]
    )

    submit = SubmitField(
        "Publish Listing"
    )