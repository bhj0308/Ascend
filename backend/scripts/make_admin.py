"""Grant (or revoke) admin on an account. Admin can't be self-assigned via signup.

    python scripts/make_admin.py you@example.com                 # local DB from .env
    python scripts/make_admin.py you@example.com --render        # the Render database
    python scripts/make_admin.py you@example.com --type founder  # revoke: back to a normal type

--render reads RENDER_DATABASE_URL from backend/.env.render.local (git-ignored).
"""

import argparse
import os
import re
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

RENDER_ENV_FILE = BACKEND_DIR / ".env.render.local"


def load_render_database_url() -> str:
    if not RENDER_ENV_FILE.exists():
        raise SystemExit(
            f"Missing {RENDER_ENV_FILE.name} — copy .env.render.example and paste "
            "Render's External Database URL."
        )
    match = re.search(
        r"""^\s*RENDER_DATABASE_URL\s*=\s*['"]?([^'"\n]+)['"]?""",
        RENDER_ENV_FILE.read_text(),
        re.MULTILINE,
    )
    if not match:
        raise SystemExit(f"RENDER_DATABASE_URL is not set in {RENDER_ENV_FILE.name}")
    return match.group(1).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email", help="email address of the account")
    parser.add_argument(
        "--type",
        default="admin",
        help="user type to set (default: admin; pass a normal type to revoke)",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="run against the Render database instead of the local one",
    )
    args = parser.parse_args()

    if args.render:
        # Set before importing app.config so the cached settings pick it up.
        os.environ["DATABASE_URL"] = load_render_database_url()
        os.environ.setdefault("SECRET_KEY", "x" * 32)

    from app.database import SessionLocal  # noqa: E402
    from app.models.user import User, UserType  # noqa: E402

    try:
        user_type = UserType(args.type)
    except ValueError:
        valid = ", ".join(t.value for t in UserType)
        raise SystemExit(f"Unknown --type {args.type!r}. Valid types: {valid}")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == args.email).first()
        if not user:
            raise SystemExit(f"No account with email {args.email}")

        previous = user.user_type.value
        if previous == user_type.value:
            print(f"{args.email} is already {previous} — nothing to do.")
            return

        user.user_type = user_type
        db.commit()
        print(f"{args.email}: {previous} -> {user_type.value}")
        if user_type == UserType.ADMIN:
            print("Sign out and back in to pick up the new role.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
