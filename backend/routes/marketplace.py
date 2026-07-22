from flask import (
    Blueprint,
    abort,
    render_template,
    request,
)

from sqlalchemy import or_

from extensions import db
from models.category import Category
from models.item import Item


marketplace = Blueprint(
    "marketplace",
    __name__,
)


CONDITION_CHOICES = [
    "Brand New",
    "Like New",
    "Good",
    "Fair",
    "Used",
]


STATUS_CHOICES = [
    "Available",
    "Reserved",
    "Sold",
]


LISTINGS_PER_PAGE = 12


@marketplace.route("/marketplace")
def marketplace_home():

    search = request.args.get(
        "search",
        "",
    ).strip()

    category_id = request.args.get(
        "category",
        type=int,
    )

    condition = request.args.get(
        "condition",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "",
    ).strip()

    minimum_price = request.args.get(
        "min_price",
        type=float,
    )

    maximum_price = request.args.get(
        "max_price",
        type=float,
    )

    sort = request.args.get(
        "sort",
        "newest",
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    page = max(
        page,
        1,
    )

    query = Item.query.filter(
        Item.status != "Removed"
    )

    if search:

        query = query.filter(
            or_(
                Item.title.ilike(
                    f"%{search}%"
                ),
                Item.description.ilike(
                    f"%{search}%"
                ),
            )
        )

    if category_id:

        query = query.filter(
            Item.category_id == category_id
        )

    if condition in CONDITION_CHOICES:

        query = query.filter(
            Item.condition == condition
        )

    if status in STATUS_CHOICES:

        query = query.filter(
            Item.status == status
        )

    if minimum_price is not None:

        query = query.filter(
            Item.price >= minimum_price
        )

    if maximum_price is not None:

        query = query.filter(
            Item.price <= maximum_price
        )

    if sort == "oldest":

        query = query.order_by(
            Item.created_at.asc()
        )

    elif sort == "price_low":

        query = query.order_by(
            Item.price.asc()
        )

    elif sort == "price_high":

        query = query.order_by(
            Item.price.desc()
        )

    else:

        sort = "newest"

        query = query.order_by(
            Item.created_at.desc()
        )

    pagination = query.paginate(
        page=page,
        per_page=LISTINGS_PER_PAGE,
        error_out=False,
    )

    listings = pagination.items

    categories = Category.query.filter_by(
        is_active=True
    ).order_by(
        Category.category_name
    ).all()

    return render_template(
        "marketplace.html",
        listings=listings,
        pagination=pagination,
        categories=categories,
        conditions=CONDITION_CHOICES,
        statuses=STATUS_CHOICES,
        search=search,
        selected_category=category_id,
        selected_condition=condition,
        selected_status=status,
        minimum_price=minimum_price,
        maximum_price=maximum_price,
        selected_sort=sort,
    )


@marketplace.route(
    "/item/<int:item_id>"
)
def item_details(item_id):

    item = db.get_or_404(
        Item,
        item_id,
    )

    if item.status == "Removed":

        abort(404)

    return render_template(
        "item_details.html",
        item=item,
    )