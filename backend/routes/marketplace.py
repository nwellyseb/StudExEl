from flask import (
    Blueprint,
    render_template,
    request,
)

from sqlalchemy import or_

from models.item import Item


marketplace = Blueprint(
    "marketplace",
    __name__
)


@marketplace.route("/marketplace")
def marketplace_home():

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = Item.query

    if search:
        query = query.filter(
            or_(
                Item.title.ilike(f"%{search}%"),
                Item.description.ilike(f"%{search}%")
            )
        )

    listings = query.order_by(
        Item.created_at.desc()
    ).all()

    return render_template(
        "marketplace.html",
        listings=listings,
        search=search
    )


@marketplace.route("/item/<int:item_id>")
def item_details(item_id):

    item = Item.query.get_or_404(
        item_id
    )

    return render_template(
        "item_details.html",
        item=item
    )