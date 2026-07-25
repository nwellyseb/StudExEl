import resend

from flask import current_app


def send_email(
    *,
    recipient,
    subject,
    html,
    text,
):

    message = {
        "from": current_app.config.get(
            "EMAIL_FROM",
            "",
        ),
        "to": [recipient],
        "subject": subject,
        "html": html,
        "text": text,
    }

    if current_app.config.get("TESTING"):

        outbox = current_app.extensions.setdefault(
            "email_outbox",
            [],
        )

        outbox.append(message)

        return {
            "id": f"test-email-{len(outbox)}"
        }

    api_key = current_app.config.get(
        "RESEND_API_KEY",
        "",
    )

    if not api_key:

        raise RuntimeError(
            "RESEND_API_KEY is not configured."
        )

    if not message["from"]:

        raise RuntimeError(
            "EMAIL_FROM is not configured."
        )

    resend.api_key = api_key

    return resend.Emails.send(
        message
    )
