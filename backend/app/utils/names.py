"""User display-name helper shared by every response schema that shows a person."""

from app.models.user import User


def display_name(user: User) -> str:
    """First + last name, falling back to the email local-part if both are empty."""
    full_name = " ".join(part for part in (user.first_name, user.last_name) if part)
    return full_name or user.email.split("@")[0]
