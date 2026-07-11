from extensions import db
from models.item import Item


def create_marketplace_item(
    app,
    user,
    category,
    title,
    description,
):

    with app.app_context():

        item = Item(
            title=title,
            description=description,
            price=350.00,
            condition="Good",
            seller_id=user.id,
            school_id=user.school_id,
            category_id=category.id,
        )

        db.session.add(item)
        db.session.commit()

        return item.id


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