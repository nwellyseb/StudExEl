from datetime import UTC, datetime
from unittest.mock import patch

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



def prepare_verification_submission(
    app,
    user_id,
):
    with app.app_context():

        student = db.session.get(
            User,
            user_id,
        )

        student.verification_status = "Pending"

        student.verification_document_public_id = (
            "studexel/verifications/test-document"
        )

        student.verification_document_format = "png"

        student.verification_submitted_at = (
            datetime.now(UTC).replace(tzinfo=None)
        )

        student.verification_rejection_reason = None

        db.session.commit()


def test_normal_user_cannot_view_student_verifications(
    client,
    user,
):
    log_in_with_session(
        client,
        user.id,
    )

    response = client.get(
        "/admin/verifications",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Administrator access is required."
        in response.data
    )


def test_admin_can_view_pending_verifications(
    client,
    app,
    user,
    second_user,
):
    make_user_admin(
        app,
        user.id,
    )

    prepare_verification_submission(
        app,
        second_user.id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    response = client.get(
        "/admin/verifications"
    )

    assert response.status_code == 200

    assert (
        b"Student Verifications"
        in response.data
    )

    assert (
        second_user.full_name.encode()
        in response.data
    )

    assert b"Pending" in response.data


def test_admin_can_open_verification_document(
    client,
    app,
    user,
    second_user,
):
    make_user_admin(
        app,
        user.id,
    )

    prepare_verification_submission(
        app,
        second_user.id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    with patch(
        "routes.moderation."
        "get_verification_document_url",
        return_value=(
            "https://example.com/"
            "signed-verification-document"
        ),
    ) as document_url:

        response = client.get(
            (
                "/admin/verifications/"
                f"{second_user.id}/document"
            ),
            follow_redirects=False,
        )

    assert response.status_code == 302

    assert response.headers["Location"] == (
        "https://example.com/"
        "signed-verification-document"
    )

    document_url.assert_called_once_with(
        "studexel/verifications/test-document",
        "png",
    )


def test_admin_can_approve_student_verification(
    client,
    app,
    user,
    second_user,
):
    make_user_admin(
        app,
        user.id,
    )

    prepare_verification_submission(
        app,
        second_user.id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    with patch(
        "routes.moderation."
        "delete_verification_document"
    ) as delete_document:

        response = client.post(
            (
                "/admin/verifications/"
                f"{second_user.id}/approve"
            ),
            follow_redirects=True,
        )

    assert response.status_code == 200

    assert (
        b"Student verification approved."
        in response.data
    )

    delete_document.assert_called_once_with(
        "studexel/verifications/test-document"
    )

    with app.app_context():

        approved_user = db.session.get(
            User,
            second_user.id,
        )

        assert (
            approved_user.verification_status
            == "Verified"
        )

        assert (
            approved_user.verification_reviewed_by_id
            == user.id
        )

        assert (
            approved_user.verification_reviewed_at
            is not None
        )

        assert (
            approved_user.verification_document_public_id
            is None
        )

        assert (
            approved_user.verification_document_format
            is None
        )


def test_admin_can_reject_student_verification(
    client,
    app,
    user,
    second_user,
):
    make_user_admin(
        app,
        user.id,
    )

    prepare_verification_submission(
        app,
        second_user.id,
    )

    log_in_with_session(
        client,
        user.id,
    )

    rejection_reason = (
        "The uploaded student ID is not readable."
    )

    with patch(
        "routes.moderation."
        "delete_verification_document"
    ) as delete_document:

        response = client.post(
            (
                "/admin/verifications/"
                f"{second_user.id}/reject"
            ),
            data={
                "reason": rejection_reason,
            },
            follow_redirects=True,
        )

    assert response.status_code == 200

    assert (
        b"Student verification rejected."
        in response.data
    )

    delete_document.assert_called_once_with(
        "studexel/verifications/test-document"
    )

    with app.app_context():

        rejected_user = db.session.get(
            User,
            second_user.id,
        )

        assert (
            rejected_user.verification_status
            == "Rejected"
        )

        assert (
            rejected_user.verification_rejection_reason
            == rejection_reason
        )

        assert (
            rejected_user.verification_reviewed_by_id
            == user.id
        )

        assert (
            rejected_user.verification_reviewed_at
            is not None
        )

        assert (
            rejected_user.verification_document_public_id
            is None
        )
