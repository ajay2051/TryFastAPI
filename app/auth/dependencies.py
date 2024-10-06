from typing import List

from fastapi import Depends, HTTPException, status

from app.auth.auth import get_current_user
from app.models import User


class RoleChecker:
    """
    Checks the roles of users.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if not current_user.is_verified:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unverified user')
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized",
            )
        return True
