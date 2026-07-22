from extensions import db
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


def create_user_report(
    app,
    reporter_id,
    reported_user_id,
    status="Pending",
    reason="Scam or fraud",
):

    with app.app_context():

        report = Report(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reason=reason,
            details=(
                "This report contains enough detail "
                "for an administrator to review."
            ),
            status=status,
        )

        db.session.add(report)
        db.session.commit()

        return report.id


def test_moderation_reports_require_login(
    client,
):

    response = client.get(
        "/admin/reports",
    )

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_normal_user_cannot_view_moderation_reports(
    client,
    user,
):

    log_in_with_session(
        client,
        user.id,
    )

    response = client.get(
        "/admin/reports",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Administrator access is required."
        in response.data
    )


def test_admin_can_view_moderation_reports(
    client,
    app,
    user,
    second_user,
):

    make_user_admin(
        app,
        user.id,
    )

    create_user_report(
        app,
        reporter_id=second_user.id,
        reported_user_id=user.id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    response = client.get(
        "/admin/reports",
    )

    assert response.status_code == 200
    assert b"Moderation Reports" in response.data
    assert b"Scam or fraud" in response.data
    assert second_user.full_name.encode() in response.data


def test_admin_can_filter_reports_by_status(
    client,
    app,
    user,
    second_user,
):

    make_user_admin(
        app,
        user.id,
    )

    create_user_report(
        app,
        reporter_id=second_user.id,
        reported_user_id=user.id,
        status="Pending",
        reason="Scam or fraud",
    )

    create_user_report(
        app,
        reporter_id=user.id,
        reported_user_id=second_user.id,
        status="Dismissed",
        reason="Spam or duplicate content",
    )

    log_in_with_session(
        client,
        user.id,
    )

    response = client.get(
        "/admin/reports?status=Dismissed",
    )

    assert response.status_code == 200
    assert b"Spam or duplicate content" in response.data
    assert b"Scam or fraud" not in response.data


def test_admin_can_update_report_status(
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
        f"/admin/reports/{report_id}/status",
        data={
            "status": "Reviewed",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Report status updated successfully."
        in response.data
    )

    with app.app_context():

        report = db.session.get(
            Report,
            report_id,
        )

        assert report.status == "Reviewed"
        assert report.reviewed_by_id == user.id
        assert report.reviewed_at is not None


def test_invalid_report_status_is_rejected(
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
        f"/admin/reports/{report_id}/status",
        data={
            "status": "Banished to the Moon",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid report status." in response.data

    with app.app_context():

        report = db.session.get(
            Report,
            report_id,
        )

        assert report.status == "Pending"
        assert report.reviewed_by_id is None
        assert report.reviewed_at is None
