import functools
from typing import List, Optional, Union

from fastapi import HTTPException, Request, status

from app.constants.messages import ERROR_MESSAGES
from app.database.sql_operations import sql_ops
from app.utils import decode_access_token


def auth_required(required_roles: Optional[Union[str, List[str]]] = None):
    """
    Authentication decorator that verifies JWT token and checks user roles.

    Args:
        required_roles: String or list of roles required to access the endpoint.
                       If None, only authentication is required.

    Usage:
        @auth_required()  # Just authentication required
        @auth_required("admin")  # Admin role required
        @auth_required(["admin", "moderator"])  # Either admin or moderator role required

    The decorator follows this flow:
    1. Extract token from Authorization header
    2. Decode JWT token to get username/email
    3. Query database to get user details
    4. Verify user exists and is active
    5. Check if user has required role(s)
    6. Inject user object into the decorated function
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from function arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found in function arguments",
                )

            # Step 1: Extract token from Authorization header
            authorization = request.headers.get("Authorization")
            if not authorization:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ERROR_MESSAGES["UNAUTHORIZED"],
                    headers={"WWW-Authenticate": "Bearer"},
                )

            try:
                scheme, token = authorization.split()
                if scheme.lower() != "bearer":
                    raise ValueError("Invalid authentication scheme")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ERROR_MESSAGES["UNAUTHORIZED"],
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Step 2: Decode JWT token to extract username/email
            email = decode_access_token(token)
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ERROR_MESSAGES["UNAUTHORIZED"],
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Step 3: Get user from database using email
            user = await sql_ops.get_user_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ERROR_MESSAGES["USER_NOT_FOUND"],
                )

            # Verify user is active
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive",
                )

            # Step 4: Check if user has required role(s)
            if required_roles is not None:
                # Convert single role to list for uniform processing
                roles_list = (
                    required_roles
                    if isinstance(required_roles, list)
                    else [required_roles]
                )

                if user.role not in roles_list:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=ERROR_MESSAGES["FORBIDDEN"],
                    )

            # Step 5: Inject user into kwargs and call the original function
            kwargs["current_user"] = user
            return await func(*args, **kwargs)

        return wrapper

    return decorator
