from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from extensions import db

from forms.item_form import (
    EditItemForm,
    ItemForm,
)

from models.category import Category
from models.item import Item
from models.user import User

from utils.decorators import login_required
from utils.uploads import (
    delete_item_image,
    save_item_image,
)


listings = Blueprint(
    "listings",
    __name__,
)


@listings.route(
    "/sell",
    methods=["GET", "POST"],
)
@login_required
def sell():

    form = ItemForm()

    categories = Category.query.order_by(
        Category.category_name
    ).all()

    form.category.choices = [
        (
            category.id,
            category.category_name,
        )
        for category in categories
    ]

    if form.validate_on_submit():

        user = db.get_or_404(
            User,
            session["user_id"],
        )

        image_filename = save_item_image(
            form.image.data
        )

        item = Item(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            condition=form.condition.data,
            image=image_filename,
            status="Available",
            seller_id=user.id,
            school_id=user.school_id,
            category_id=form.category.data,
        )

        db.session.add(item)
        db.session.commit()

        flash(
            "Your item has been listed!",
            "success",
        )

        return redirect(
            url_for(
                "marketplace.marketplace_home"
            )
        )

    return render_template(
        "sell.html",
        form=form,
    )


@listings.route("/my-listings")
@login_required
def my_listings():

    listings_data = Item.query.filter_by(
        seller_id=session["user_id"]
    ).order_by(
        Item.created_at.desc()
    ).all()

    return render_template(
        "my_listings.html",
        listings=listings_data,
    )


@listings.route(
    "/edit/<int:item_id>",
    methods=["GET", "POST"],
)
@login_required
def edit_item(item_id):

    item = db.get_or_404(
        Item,
        item_id,
    )

    if item.seller_id != session["user_id"]:

        flash(
            "You cannot edit this item.",
            "danger",
        )

        return redirect(
            url_for(
                "marketplace.marketplace_home"
            )
        )

    form = EditItemForm()

    categories = Category.query.order_by(
        Category.category_name
    ).all()

    form.category.choices = [
        (
            category.id,
            category.category_name,
        )
        for category in categories
    ]

    if request.method == "GET":

        form.title.data = item.title
        form.description.data = item.description
        form.price.data = item.price
        form.condition.data = item.condition
        form.category.data = item.category_id
        form.status.data = item.status

    if form.validate_on_submit():

        item.title = form.title.data
        item.description = form.description.data
        item.price = form.price.data
        item.condition = form.condition.data
        item.category_id = form.category.data
        item.status = form.status.data

        old_image_filename = None

        if (
            form.image.data
            and form.image.data.filename
        ):

            old_image_filename = item.image

            item.image = save_item_image(
                form.image.data
            )

        db.session.commit()

        if old_image_filename:

            delete_item_image(
                old_image_filename
            )

        flash(
            "Listing updated successfully!",
            "success",
        )

        return redirect(
            url_for(
                "listings.my_listings"
            )
        )

    return render_template(
        "edit_item.html",
        form=form,
        item=item,
    )


@listings.route(
    "/delete/<int:item_id>",
    methods=["POST"],
)
@login_required
def delete_item(item_id):

    item = db.get_or_404(
        Item,
        item_id,
    )

    if item.seller_id != session["user_id"]:

        flash(
            "You cannot delete this item.",
            "danger",
        )

        return redirect(
            url_for(
                "listings.my_listings"
            )
        )

    image_filename = item.image

    db.session.delete(item)
    db.session.commit()

    delete_item_image(
        image_filename
    )

    flash(
        "Listing deleted successfully!",
        "success",
    )

    return redirect(
        url_for(
            "listings.my_listings"
        )
    )