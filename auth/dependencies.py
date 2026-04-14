from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from jose import JWTError

from .models import TokenPayload
from .security import decode_access_token

_bearer = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> TokenPayload:
    """
    Dependência que valida o Bearer token e retorna o payload.
    Usar como: current_user: TokenPayload = Depends(get_current_user)
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError:
        raise exc

    return payload


def require_accountant(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    """Restringe o endpoint apenas a contadores."""
    if current_user.user_type != "accountant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a contadores.",
        )
    return current_user


def require_client_admin(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    """Restringe o endpoint a client-admin ou accountant."""
    if current_user.role not in ("accountant", "client-admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )
    return current_user


def require_same_client(
    client_id: int,
    current_user: TokenPayload = Depends(get_current_user),
) -> TokenPayload:
    """
    Garante que um client_user só acessa dados do próprio client_id.
    Contadores têm acesso irrestrito.
    """
    if current_user.user_type == "accountant":
        return current_user

    if current_user.client_id != client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a este cliente.",
        )
    return current_user
