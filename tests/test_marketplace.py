from extensions import db
from models.category import Category
from models.item import Item


def create_marketplace_item(
    app,
    user,
    category,
    title,
    description,
    price=350.00,
    condition="Good",
    status="Available",
):

    with app.app_context():

        item = Item(
            title=title,
            description=description,
            price=price,
            condition=condition,
            status=status,
            seller_id=user.id,
            school_id=user.school_id,
            category_id=category.id,
        )

        db.session.add(item)
        db.session.commit()

        return item.id


def create_marketplace_category(
    app,
    name,
    slug,
):

    with app.app_context():

        category = Category(
            category_name=name,
            slug=slug,
            description=f"{name} marketplace category.",
            display_order=2,
            is_active=True,
        )

        db.session.add(category)
        db.session.commit()

        return category.id


def test_search_finds_matching_listing(
    client,
    app,
    user,
    category,
):

    create_marketplace_item(
        app,
        user,
        category,
        title="Calculus Textbook",
        description=(
            "A mathematics textbook "
            "for first-year students."
        ),
    )

    create_marketplace_item(
        app,
        user,
        category,
        title="Wireless Keyboard",
        description=(
            "A compact keyboard for studying."
        ),
    )

    response = client.get(
        "/marketplace?search=Calculus"
    )

    assert response.status_code == 200

    assert (
        b"Calculus Textbook"
        in response.data
    )

    assert (
        b"Wireless Keyboard"
        not in response.data
    )


def test_search_matches_description(
    client,
    app,
    user,
    category,
):

    create_marketplace_item(
        app,
        user,
        category,
        title="Physics Reference Book",
        description=(
            "Includes detailed calculus examples "
            "and practice exercises."
        ),
    )

    response = client.get(
        "/marketplace?search=calculus"
    )

    assert response.status_code == 200

    assert (
        b"Physics Reference Book"
        in response.data
    )


def test_search_with_no_matches_shows_message(
    client,
):

    response = client.get(
        "/marketplace?search=nonexistentitem"
    )

    assert response.status_code == 200

    assert (
        b"No listings matched your search."
        in response.data
    )


def test_category_filter(
    client,
    app,
    user,
    category,
):

    electronics_id = create_marketplace_category(
        app,
        name="Electronics",
        slug="electronics",
    )

    with app.app_context():

        electronics = db.session.get(
            Category,
            electronics_id,
        )

        create_marketplace_item(
            app,
            user,
            category,
            title="Programming Textbook",
            description=(
                "A textbook about software development."
            ),
        )

        create_marketplace_item(
            app,
            user,
            electronics,
            title="Mechanical Keyboard",
            description=(
                "A keyboard suitable for studying."
            ),
        )

    response = client.get(
        f"/marketplace?category={category.id}"
    )

    assert response.status_code == 200

    assert (
        b"Programming Textbook"
        in response.data
    )

    assert (
        b"Mechanical Keyboard"
        not in response.data
    )


def test_condition_filter(
    client,
    app,
    user,
    category,
):

    create_marketplace_item(
        app,
        user,
        category,
        title="Good Condition Book",
        description=(
            "A book kept in good condition."
        ),
        condition="Good",
    )

    create_marketplace_item(
        app,
        user,
        category,
        title="Used Condition Book",
        description=(
            "A book with visible signs of use."
        ),
        condition="Used",
    )

    response = client.get(
        "/marketplace?condition=Used"
    )

    assert response.status_code == 200

    assert (
        b"Used Condition Book"
        in response.data
    )

    assert (
        b"Good Condition Book"
        not in response.data
    )


def test_status_filter(
    client,
    app,
    user,
    category,
):

    create_marketplace_item(
        app,
        user,
        category,
        title="Available Calculator",
        description=(
            "A calculator available for purchase."
        ),
        status="Available",
    )

    create_marketplace_item(
        app,
        user,
        category,
        title="Reserved Calculator",
        description=(
            "A calculator reserved by another student."
        ),
        status="Reserved",
    )

    response = client.get(
        "/marketplace?status=Reserved"
    )

    assert response.status_code == 200

    assert (
        b"Reserved Calculator"
        in response.data
    )

    assert (
        b"Available Calculator"
        not in response.data
    )


def test_price_range_filter(
    client,
    app,
    user,
    category,
):

    create_marketplace_item(
        app,
        user,
        category,
        title="Low Price Item",
        description=(
            "An inexpensive marketplace item."
        ),
        price=100.00,
    )

    create_marketplace_item(
        app,
        user,
        category,
        title="Mid Price Item",
        description=(
            "A moderately priced marketplace item."
        ),
        price=500.00,
    )

    create_marketplace_item(
        app,
        user,
        category,
        title="High Price Item",
        description=(
            "An expensive marketplace item."
        ),
        price=1000.00,
    )

    response = client.get(
        "/marketplace?min_price=200&max_price=700"
    )

    assert response.status_code == 200

    assert (
        b"Mid Price Item"
        in response.data
    )

    assert (
        b"Low Price Item"
        not in response.data
    )

    assert (
        b"High Price Item"
        not in response.data
    )


def test_price_sort_low_to_high(
    client,
    app,
    user,
    category,
):

    create_marketplace_item(
        app,
        user,
        category,
        title="Premium Item",
        description=(
            "A high-priced marketplace item."
        ),
        price=900.00,
    )

    create_marketplace_item(
        app,
        user,
        category,
        title="Budget Item",
        description=(
            "A low-priced marketplace item."
        ),
        price=100.00,
    )

    response = client.get(
        "/marketplace?sort=price_low"
    )

    assert response.status_code == 200

    budget_position = response.data.find(
        b"Budget Item"
    )

    premium_position = response.data.find(
        b"Premium Item"
    )

    assert budget_position != -1
    assert premium_position != -1
    assert budget_position < premium_position


def test_item_details_page_loads(
    client,
    app,
    user,
    category,
):

    item_id = create_marketplace_item(
        app,
        user,
        category,
        title="Discrete Mathematics Book",
        description=(
            "A reference book for discrete "
            "mathematics and logic."
        ),
    )

    response = client.get(
        f"/item/{item_id}"
    )

    assert response.status_code == 200

    assert (
        b"Discrete Mathematics Book"
        in response.data
    )

    assert (
        b"A reference book for discrete"
        in response.data
    )


def test_missing_item_returns_404(
    client,
):

    response = client.get(
        "/item/999999"
    )

    assert response.status_code == 404

def test_marketplace_pagination(
    client,
    app,
    user,
    category,
):

    for number in range(1, 14):

        create_marketplace_item(
            app,
            user,
            category,
            title=f"Pagination Item {number:02d}",
            description=(
                f"Marketplace pagination test item "
                f"number {number}."
            ),
            price=float(number),
        )

    first_page = client.get(
        "/marketplace?sort=price_low&page=1"
    )

    assert first_page.status_code == 200

    assert (
        b"Pagination Item 01"
        in first_page.data
    )

    assert (
        b"Pagination Item 12"
        in first_page.data
    )

    assert (
        b"Pagination Item 13"
        not in first_page.data
    )

    second_page = client.get(
        "/marketplace?sort=price_low&page=2"
    )

    assert second_page.status_code == 200

    assert (
        b"Pagination Item 13"
        in second_page.data
    )

    assert (
        b"Pagination Item 01"
        not in second_page.data
    )
