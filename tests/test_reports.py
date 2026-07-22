from extensions import db
from models.item import Item
from models.report import Report


def log_in_with_session(
    client,
    user_id,
):

    with client.session_transaction() as session:
        session["user_id"] = user_id


def create_report_test_item(
    app,
    seller,
    category,
    status="Available",
):

    with app.app_context():

        item = Item(
            title="Report Test Listing",
            description=(
                "A marketplace listing used for "
                "reporting tests."
            ),
            price=500.00,
            condition="Good",
            status=status,
            seller_id=seller.id,
            category_id=category.id,
            school_id=seller.school_id,
        )

        db.session.add(item)
        db.session.commit()

        return item.id


def test_report_listing_requires_login(
    client,
    app,
    user,
    category,
):

    item_id = create_report_test_item(
        app,
        seller=user,
        category=category,
    )

    response = client.get(
        f"/reports/item/{item_id}",
    )

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_user_can_view_listing_report_form(
    client,
    app,
    user,
    second_user,
    category,
):

    item_id = create_report_test_item(
        app,
        seller=user,
        category=category,
    )

    log_in_with_session(
        client,
        second_user.id,
    )

    response = client.get(
        f"/reports/item/{item_id}",
    )

    assert response.status_code == 200
    assert b"Report Listing" in response.data
    assert b"Report Test Listing" in response.data


def test_user_can_submit_listing_report(
    client,
    app,
    user,
    second_user,
    category,
):

    item_id = create_report_test_item(
        app,
        seller=user,
        category=category,
    )

    log_in_with_session(
        client,
        second_user.id,
    )

    response = client.post(
        f"/reports/item/{item_id}",
        data={
            "reason": "Scam or fraud",
            "details": (
                "The seller requested payment outside "
                "the marketplace."
            ),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Listing report submitted successfully."
        in response.data
    )

    with app.app_context():

        report = Report.query.filter_by(
            reporter_id=second_user.id,
            reported_item_id=item_id,
        ).first()

        assert report is not None
        assert report.reason == "Scam or fraud"
        assert report.status == "Pending"
        assert report.reported_user_id is None


def test_user_cannot_report_own_listing(
    client,
    app,
    user,
    category,
):

    item_id = create_report_test_item(
        app,
        seller=user,
        category=category,
    )

    log_in_with_session(
        client,
        user.id,
    )

    response = client.get(
        f"/reports/item/{item_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"You cannot report your own listing." in response.data

    with app.app_context():

        report_count = Report.query.filter_by(
            reporter_id=user.id,
            reported_item_id=item_id,
        ).count()

        assert report_count == 0


def test_duplicate_pending_listing_report_is_blocked(
    client,
    app,
    user,
    second_user,
    category,
):

    item_id = create_report_test_item(
        app,
        seller=user,
        category=category,
    )

    with app.app_context():

        report = Report(
            reporter_id=second_user.id,
            reported_item_id=item_id,
            reason="Misleading information",
            details=(
                "The listing description does not "
                "match the advertised item."
            ),
            status="Pending",
        )

        db.session.add(report)
        db.session.commit()

    log_in_with_session(
        client,
        second_user.id,
    )

    response = client.get(
        f"/reports/item/{item_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"You already have a pending report "
        b"for this listing."
        in response.data
    )

    with app.app_context():

        report_count = Report.query.filter_by(
            reporter_id=second_user.id,
            reported_item_id=item_id,
            status="Pending",
        ).count()

        assert report_count == 1


def test_user_cannot_report_self(
    client,
    user,
):

    log_in_with_session(
        client,
        user.id,
    )

    response = client.get(
        f"/reports/user/{user.id}",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"You cannot report yourself." in response.data


def test_user_can_submit_user_report(
    client,
    app,
    user,
    second_user,
):

    log_in_with_session(
        client,
        second_user.id,
    )

    response = client.post(
        f"/reports/user/{user.id}",
        data={
            "reason": "Harassment or abusive behavior",
            "details": (
                "The user repeatedly sent abusive "
                "messages during the conversation."
            ),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"User report submitted successfully."
        in response.data
    )

    with app.app_context():

        report = Report.query.filter_by(
            reporter_id=second_user.id,
            reported_user_id=user.id,
        ).first()

        assert report is not None
        assert (
            report.reason
            == "Harassment or abusive behavior"
        )
        assert report.status == "Pending"
        assert report.reported_item_id is None
