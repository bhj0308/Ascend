"""User display-name helper shared by every response schema that shows a person."""

from app.models.user import User


def display_name(user: User) -> str:
    """First + last name, or "User #<id>" when both are empty.

    Never falls back to the email or its local-part: other users must not learn
    any part of someone's address from a name field (see the Privacy page).
    """
    full_name = " ".join(part for part in (user.first_name, user.last_name) if part)
    return full_name or f"User #{user.id}"
