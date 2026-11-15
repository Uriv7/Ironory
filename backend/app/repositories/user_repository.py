from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository handling persistence operations for User entities."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        normalized_email = email.strip().lower()
        return self.db.query(User).filter(User.email == normalized_email).first()

    def create_user(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        is_super_admin: bool = False,
        is_active: bool = True
    ) -> User:
        user = User(
            email=email.strip().lower(),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            is_super_admin=is_super_admin,
            is_active=is_active
        )
        return self.create(user)
