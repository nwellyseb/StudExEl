from extensions import db

from models.conversation import Conversation
from models.item import Item
from models.message import Message
from models.user import User


def create_message_test_item(
    app,
    seller,
    category,
    status="Available",
):

    with app.app_context():

        item = Item(
            title="Messaging Test Textbook",
            description=(
                "A textbook listing used for "
                "testing private conversations."
            ),
            price=450.00,
            condition="Good",
            status=status,
            seller_id=seller.id,
            school_id=seller.school_id,
            category_id=category.id,
        )

        db.session.add(item)
        db.session.commit()

        return item.id


def create_test_conversation(
    app,
    item_id,
    buyer_id,
    seller_id,
):

    with app.app_context():

        conversation = Conversation(
            item_id=item_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
        )

        db.session.add(conversation)
        db.session.commit()

        return conversation.id


def login_user(
    client,
    username,
    password,
):

    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=True,
    )


def test_messages_inbox_requires_login(
    client,
):

    response = client.get(
        "/messages",
        follow_redirects=False,
    )

    assert response.status_code == 302

    assert (
        "/login"
        in response.headers["Location"]
    )


def test_buyer_can_start_conversation(
    client,
    app,
    user,
    second_user,
    category,
):

    item_id = create_message_test_item(
        app,
        seller=user,
        category=category,
    )

    login_user(
        client,
        second_user.username,
        "anotherpassword123",
    )

    response = client.post(
        f"/messages/start/{item_id}",
        follow_redirects=False,
    )

    assert response.status_code == 302

    with app.app_context():

        conversation = Conversation.query.filter_by(
            item_id=item_id,
            buyer_id=second_user.id,
            seller_id=user.id,
        ).first()

        assert conversation is not None

        assert (
            f"/messages/{conversation.id}"
            in response.headers["Location"]
        )


def test_starting_same_conversation_twice_does_not_duplicate(
    client,
    app,
    user,
    second_user,
    category,
):

    item_id = create_message_test_item(
        app,
        seller=user,
        category=category,
    )

    login_user(
        client,
        second_user.username,
        "anotherpassword123",
    )

    first_response = client.post(
        f"/messages/start/{item_id}",
        follow_redirects=False,
    )

    second_response = client.post(
        f"/messages/start/{item_id}",
        follow_redirects=False,
    )

    assert first_response.status_code == 302
    assert second_response.status_code == 302

    with app.app_context():

        conversations = Conversation.query.filter_by(
            item_id=item_id,
            buyer_id=second_user.id,
            seller_id=user.id,
        ).all()

        assert len(conversations) == 1


def test_seller_cannot_message_own_listing(
    logged_in_client,
    app,
    user,
    category,
):

    item_id = create_message_test_item(
        app,
        seller=user,
        category=category,
    )

    response = logged_in_client.post(
        f"/messages/start/{item_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"You cannot message yourself "
        b"about your own listing."
        in response.data
    )

    with app.app_context():

        assert (
            Conversation.query.count()
            == 0
        )


def test_buyer_cannot_start_conversation_for_sold_item(
    client,
    app,
    user,
    second_user,
    category,
):

    item_id = create_message_test_item(
        app,
        seller=user,
        category=category,
        status="Sold",
    )

    login_user(
        client,
        second_user.username,
        "anotherpassword123",
    )

    response = client.post(
        f"/messages/start/{item_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"This item has already been sold."
        in response.data
    )

    with app.app_context():

        assert (
            Conversation.query.count()
            == 0
        )


def test_participant_can_send_message(
    client,
    app,
    user,
    second_user,
    category,
):

    item_id = create_message_test_item(
        app,
        seller=user,
        category=category,
    )

    conversation_id = create_test_conversation(
        app,
        item_id=item_id,
        buyer_id=second_user.id,
        seller_id=user.id,
    )

    login_user(
        client,
        second_user.username,
        "anotherpassword123",
    )

    response = client.post(
        f"/messages/{conversation_id}",
        data={
            "body": (
                "Hello, is this textbook "
                "still available?"
            ),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Hello, is this textbook "
        b"still available?"
        in response.data
    )

    with app.app_context():

        message = Message.query.filter_by(
            conversation_id=conversation_id,
            sender_id=second_user.id,
        ).first()

        assert message is not None

        assert message.body == (
            "Hello, is this textbook "
            "still available?"
        )

        assert message.is_read is False


def test_non_participant_cannot_access_conversation(
    client,
    app,
    school,
    user,
    second_user,
    category,
):

    item_id = create_message_test_item(
        app,
        seller=user,
        category=category,
    )

    conversation_id = create_test_conversation(
        app,
        item_id=item_id,
        buyer_id=second_user.id,
        seller_id=user.id,
    )

    with app.app_context():

        outsider = User(
            first_name="Outside",
            last_name="Student",
            username="outsidestudent",
            email="outsidestudent@example.com",
            school_id=school.id,
        )

        outsider.set_password(
            "outsidepassword123"
        )

        db.session.add(outsider)
        db.session.commit()

    login_user(
        client,
        "outsidestudent",
        "outsidepassword123",
    )

    response = client.get(
        f"/messages/{conversation_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"You cannot access this conversation."
        in response.data
    )

    assert (
        b"Hello, is this textbook still available?"
        not in response.data
    )


def test_opening_conversation_marks_received_messages_read(
    client,
    app,
    user,
    second_user,
    category,
):

    item_id = create_message_test_item(
        app,
        seller=user,
        category=category,
    )

    conversation_id = create_test_conversation(
        app,
        item_id=item_id,
        buyer_id=second_user.id,
        seller_id=user.id,
    )

    with app.app_context():

        message = Message(
            conversation_id=conversation_id,
            sender_id=second_user.id,
            body=(
                "I am interested in buying "
                "this textbook."
            ),
            is_read=False,
        )

        db.session.add(message)
        db.session.commit()

        message_id = message.id

    login_user(
        client,
        user.username,
        "securepassword123",
    )

    response = client.get(
        f"/messages/{conversation_id}"
    )

    assert response.status_code == 200

    assert (
        b"I am interested in buying "
        b"this textbook."
        in response.data
    )

    with app.app_context():

        saved_message = db.session.get(
            Message,
            message_id,
        )

        assert saved_message.is_read is True