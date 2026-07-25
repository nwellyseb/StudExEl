import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import app
from extensions import db
from models.user import User


def promote_admin():
    admin_email = os.environ.get("ADMIN_EMAIL", "").strip().lower()

    if not admin_email:
        print("ADMIN_EMAIL is not set. Skipping administrator promotion.")
        return

    with app.app_context():
        user = User.query.filter(
            db.func.lower(User.email) == admin_email
        ).first()

        if user is None:
            print(f"No user found with email: {admin_email}")
            return

        if user.is_admin:
            print(f"{user.email} is already an administrator.")
            return

        user.is_admin = True
        db.session.commit()

        print(f"Promoted {user.email} to administrator.")


if __name__ == "__main__":
    promote_admin()
