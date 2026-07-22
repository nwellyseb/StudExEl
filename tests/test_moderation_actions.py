from flask import url_for

from extensions import db
from models.item import Item
from models.report import Report
from models.user import User


def log_in_with_session(
    client,
    user_id,
):

    with client.session_transaction() as session:
        session["user_id"] = user_id


def make_user_admin(
    app,
    user_id,
):

    with app.app_context():

        user = db.session.get(
            User,
            user_id,
        )

        user.is_admin = True
        db.session.commit()


def create_item(
    app,
    seller_id,
    school_id,
    category_id,
    status="Available",
):

    with app.app_context():

        item = Item(
            title="Moderation Test Listing",
            description=(
                "A listing created for moderation "
                "action tests."
            ),
            price=250.00,
            condition="Good",
            image=None,
            status=status,
            seller_id=seller_id,
            school_id=school_id,
            category_id=category_id,
        )

        db.session.add(item)
        db.session.commit()

        return item.id


def create_item_report(
    app,
    reporter_id,
    item_id,
):

    with app.app_context():

        report = Report(
            reporter_id=reporter_id,
            reported_item_id=item_id,
            reason="Misleading information",
            details=(
                "This listing contains enough detail "
                "for an administrator to investigate."
            ),
            status="Pending",
        )

        db.session.add(report)
        db.session.commit()

        return report.id


def create_user_report(
    app,
    reporter_id,
    reported_user_id,
):

    with app.app_context():

        report = Report(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reason="Harassment or abusive behavior",
            details=(
                "This user report contains enough detail "
                "for an administrator to investigate."
            ),
            status="Pending",
        )

        db.session.add(report)
        db.session.commit()

        return report.id


def route_url(
    app,
    endpoint,
    **values,
):

    with app.test_request_context():
        return url_for(
            endpoint,
            **values,
        )


def test_admin_can_remove_reported_listing(
    client,
    app,
    user,
    second_user,
    school,
    category,
):

    make_user_admin(
        app,
        user.id,
    )

    item_id = create_item(
        app,
        seller_id=second_user.id,
        school_id=school.id,
        category_id=category.id,
    )

    report_id = create_item_report(
        app,
        reporter_id=user.id,
        item_id=item_id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    response = client.post(
        f"/admin/reports/{report_id}/remove-listing",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Listing removed successfully." in response.data

    with app.app_context():

        item = db.session.get(
            Item,
            item_id,
        )

        report = db.session.get(
            Report,
            report_id,
        )

        assert item.status == "Removed"
        assert report.status == "Actioned"
        assert report.reviewed_by_id == user.id
        assert report.reviewed_at is not None


def test_removed_listing_returns_404(
    client,
    app,
    user,
    second_user,
    school,
    category,
):

    make_user_admin(
        app,
        user.id,
    )

    item_id = create_item(
        app,
        seller_id=second_user.id,
        school_id=school.id,
        category_id=category.id,
    )

    report_id = create_item_report(
        app,
        reporter_id=user.id,
        item_id=item_id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    client.post(
        f"/admin/reports/{report_id}/remove-listing",
    )

    response = client.get(
        route_url(
            app,
            "marketplace.item_details",
            item_id=item_id,
        )
    )

    assert response.status_code == 404


def test_owner_cannot_edit_or_delete_removed_listing(
    client,
    app,
    user,
    second_user,
    school,
    category,
):

    make_user_admin(
        app,
        user.id,
    )

    item_id = create_item(
        app,
        seller_id=second_user.id,
        school_id=school.id,
        category_id=category.id,
    )

    report_id = create_item_report(
        app,
        reporter_id=user.id,
        item_id=item_id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    client.post(
        f"/admin/reports/{report_id}/remove-listing",
    )

    log_in_with_session(
        client,
        second_user.id,
    )

    edit_response = client.get(
        route_url(
            app,
            "listings.edit_item",
            item_id=item_id,
        ),
        follow_redirects=True,
    )

    delete_response = client.post(
        route_url(
            app,
            "listings.delete_item",
            item_id=item_id,
        ),
        follow_redirects=True,
    )

    assert edit_response.status_code == 200
    assert (
        b"This listing was removed by an administrator."
        in edit_response.data
    )

    assert delete_response.status_code == 200
    assert (
        b"This listing was removed by an administrator."
        in delete_response.data
    )

    with app.app_context():

        item = db.session.get(
            Item,
            item_id,
        )

        assert item is not None
        assert item.status == "Removed"


def test_admin_can_suspend_reported_user(
    client,
    app,
    user,
    second_user,
):

    make_user_admin(
        app,
        user.id,
    )

    report_id = create_user_report(
        app,
        reporter_id=user.id,
        reported_user_id=second_user.id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    response = client.post(
        f"/admin/reports/{report_id}/suspend-user",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"User suspended successfully." in response.data

    with app.app_context():

        suspended_user = db.session.get(
            User,
            second_user.id,
        )

        report = db.session.get(
            Report,
            report_id,
        )

        assert suspended_user.is_active is False
        assert report.status == "Actioned"
        assert report.reviewed_by_id == user.id
        assert report.reviewed_at is not None


def test_suspended_user_cannot_log_in(
    client,
    app,
    second_user,
):

    with app.app_context():

        user = db.session.get(
            User,
            second_user.id,
        )

        user.is_active = False
        db.session.commit()

    response = client.post(
        "/login",
        data={
            "username": second_user.username,
            "password": "anotherpassword123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Your account has been suspended."
        in response.data
    )

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_suspended_existing_session_is_cleared(
    client,
    app,
    second_user,
):

    log_in_with_session(
        client,
        second_user.id,
    )

    with app.app_context():

        user = db.session.get(
            User,
            second_user.id,
        )

        user.is_active = False
        db.session.commit()

    response = client.get(
        "/my-listings",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Your account has been suspended."
        in response.data
    )

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_admin_can_reactivate_user(
    client,
    app,
    user,
    second_user,
):

    make_user_admin(
        app,
        user.id,
    )

    with app.app_context():

        suspended_user = db.session.get(
            User,
            second_user.id,
        )

        suspended_user.is_active = False
        db.session.commit()

    log_in_with_session(
        client,
        user.id,
    )

    response = client.post(
        f"/admin/users/{second_user.id}/reactivate",
        follow_redirects=True,
    )

    assert response.status_code == 200
    with app.app_context():

        reactivated_user = db.session.get(
            User,
            second_user.id,
        )

        assert reactivated_user.is_active is True


def test_normal_user_cannot_remove_reported_listing(
    client,
    app,
    user,
    second_user,
    school,
    category,
):

    item_id = create_item(
        app,
        seller_id=second_user.id,
        school_id=school.id,
        category_id=category.id,
    )

    report_id = create_item_report(
        app,
        reporter_id=user.id,
        item_id=item_id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    response = client.post(
        f"/admin/reports/{report_id}/remove-listing",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Administrator access is required."
        in response.data
    )

    with app.app_context():

        item = db.session.get(
            Item,
            item_id,
        )

        report = db.session.get(
            Report,
            report_id,
        )

        assert item.status == "Available"
        assert report.status == "Pending"


def test_admin_cannot_suspend_self(
    client,
    app,
    user,
    second_user,
):

    make_user_admin(
        app,
        user.id,
    )

    report_id = create_user_report(
        app,
        reporter_id=second_user.id,
        reported_user_id=user.id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    response = client.post(
        f"/admin/reports/{report_id}/suspend-user",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"You cannot suspend your own account."
        in response.data
    )

    with app.app_context():

        admin = db.session.get(
            User,
            user.id,
        )

        report = db.session.get(
            Report,
            report_id,
        )

        assert admin.is_active is True
        assert report.status == "Pending"


def test_admin_cannot_suspend_another_admin(
    client,
    app,
    user,
    second_user,
):

    make_user_admin(
        app,
        user.id,
    )

    make_user_admin(
        app,
        second_user.id,
    )

    report_id = create_user_report(
        app,
        reporter_id=user.id,
        reported_user_id=second_user.id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    response = client.post(
        f"/admin/reports/{report_id}/suspend-user",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():

        protected_admin = db.session.get(
            User,
            second_user.id,
        )

        report = db.session.get(
            Report,
            report_id,
        )

        assert protected_admin.is_active is True
        assert report.status == "Pending"
