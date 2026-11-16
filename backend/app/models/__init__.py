"""ORM models. Import every model here so init_db() registers them."""
from app.models.user import User

__all__ = ["User"]
