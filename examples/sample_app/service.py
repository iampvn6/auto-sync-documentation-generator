"""Service layer with decorated and async members."""


def cached(func):
    """Example decorator."""
    return func


def require_auth(func):
    """Example decorator."""
    return func


@require_auth
async def create_user(name: str, active: bool = True) -> dict:
    """Create a new user account."""
    return {"name": name, "active": active}


class UserService:
    """Manage user records."""

    @cached
    def get_user(self, user_id: int) -> dict | None:
        """Fetch a single user."""
        return None
