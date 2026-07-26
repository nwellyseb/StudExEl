import json
import os
from urllib import error, request

from flask import current_app


BREVO_EMAIL_ENDPOINT = (
    "https://api.brevo.com/v3/smtp/email"
)


def send_email(
    *,
    recipient,
    subject,
    html,
    text,
):
    test_message = {
        "from": current_app.config.get(
            "BREVO_FROM_EMAIL",
            os.getenv("BREVO_FROM_EMAIL", ""),
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

        outbox.append(test_message)

        return {
            "id": f"test-email-{len(outbox)}"
        }

    api_key = (
        current_app.config.get("BREVO_API_KEY")
        or os.getenv("BREVO_API_KEY", "")
    )

    sender_email = (
        current_app.config.get("BREVO_FROM_EMAIL")
        or os.getenv("BREVO_FROM_EMAIL", "")
    )

    sender_name = (
        current_app.config.get("BREVO_FROM_NAME")
        or os.getenv("BREVO_FROM_NAME", "StudExEl")
    )

    if not api_key:
        raise RuntimeError(
            "BREVO_API_KEY is not configured."
        )

    if not sender_email:
        raise RuntimeError(
            "BREVO_FROM_EMAIL is not configured."
        )

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [
            {
                "email": recipient,
            }
        ],
        "subject": subject,
    }

    if html:
        payload["htmlContent"] = html
    elif text:
        payload["textContent"] = text
    else:
        raise RuntimeError(
            "Email content is empty."
        )

    email_request = request.Request(
        BREVO_EMAIL_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(
            email_request,
            timeout=20,
        ) as response:
            response_data = json.loads(
                response.read().decode("utf-8")
            )

    except error.HTTPError as exc:
        response_body = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"Brevo rejected the email "
            f"with status {exc.code}: "
            f"{response_body}"
        ) from exc

    except error.URLError as exc:
        raise RuntimeError(
            f"Could not connect to Brevo: "
            f"{exc.reason}"
        ) from exc

    return {
        "id": response_data.get("messageId")
    }
