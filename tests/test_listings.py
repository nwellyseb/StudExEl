from extensions import db
from models.item import Item


def create_test_item(
    app,
    user,
    category,
):

    with app.app_context():

        item = Item(
            title="Original Textbook",
            description=(
                "An original textbook listing "
                "created for automated testing."
            ),
            price=400.00,
            condition="Good",
            seller_id=user.id,
            school_id=user.school_id,
            category_id=category.id,
        )

        db.session.add(item)
        db.session.commit()

        return item.id


def test_logged_in_user_can_create_listing(
    logged_in_client,
    app,
    user,
    category,
):

    response = logged_in_client.post(
        "/sell",
        data={
            "title": "Calculus Textbook",
            "description": (
                "A well-maintained calculus textbook "
                "for first-year students."
            ),
            "price": "450.00",
            "condition": "Good",
            "category": str(category.id),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Your item has been listed!"
        in response.data
    )

    with app.app_context():

        item = Item.query.filter_by(
            title="Calculus Textbook"
        ).first()

        assert item is not None

        assert item.description == (
            "A well-maintained calculus textbook "
            "for first-year students."
        )

        assert item.price == 450.00
        assert item.condition == "Good"
        assert item.category_id == category.id
        assert item.seller_id == user.id
        assert item.school_id == user.school_id
        assert item.image is None


def test_owner_can_edit_listing(
    logged_in_client,
    app,
    user,
    category,
):

    item_id = create_test_item(
        app,
        user,
        category,
    )

    response = logged_in_client.post(
        f"/edit/{item_id}",
        data={
            "title": "Updated Textbook",
            "description": (
                "This textbook description "
                "has been updated successfully."
            ),
            "price": "550.00",
            "condition": "Like New",
            "category": str(category.id),
            "status": "Available",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Listing updated successfully!"
        in response.data
    )

    with app.app_context():

        item = db.session.get(
            Item,
            item_id,
        )

        assert item is not None
        assert item.title == "Updated Textbook"
        assert item.price == 550.00
        assert item.condition == "Like New"

        assert item.description == (
            "This textbook description "
            "has been updated successfully."
        )


def test_owner_can_delete_listing(
    logged_in_client,
    app,
    user,
    category,
):

    item_id = create_test_item(
        app,
        user,
        category,
    )

    response = logged_in_client.post(
        f"/delete/{item_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Listing deleted successfully!"
        in response.data
    )

    with app.app_context():

        deleted_item = db.session.get(
            Item,
            item_id,
        )

        assert deleted_item is None


def test_other_user_cannot_edit_listing(
    second_logged_in_client,
    app,
    user,
    category,
):

    item_id = create_test_item(
        app,
        user,
        category,
    )

    response = second_logged_in_client.post(
        f"/edit/{item_id}",
        data={
            "title": "Unauthorized Change",
            "description": (
                "Another user should not be able "
                "to change this listing."
            ),
            "price": "1.00",
            "condition": "Fair",
            "category": str(category.id),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"You cannot edit this item."
        in response.data
    )

    with app.app_context():

        item = db.session.get(
            Item,
            item_id,
        )

        assert item is not None
        assert item.title == "Original Textbook"
        assert item.price == 400.00
        assert item.seller_id == user.id


def test_other_user_cannot_delete_listing(
    second_logged_in_client,
    app,
    user,
    category,
):

    item_id = create_test_item(
        app,
        user,
        category,
    )

    response = second_logged_in_client.post(
        f"/delete/{item_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"You cannot delete this item."
        in response.data
    )

    with app.app_context():

        item = db.session.get(
            Item,
            item_id,
        )

        assert item is not None
        assert item.seller_id == user.id