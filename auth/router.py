from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from pymysql.connections import Connection

from .db import (
    db_cleanup_expired_tokens,
    db_create_accountant,
    db_delete_accountant,
    db_get_accountant_by_email,
    db_get_accountant_by_id,
    db_get_all_accountants,
    db_get_client_user_by_email,
    db_get_refresh_token,
    db_revoke_all_user_tokens,
    db_revoke_refresh_token,
    db_save_refresh_token,
    db_update_accountant,
    db_update_accountant_password,
    db_update_client_user_password,
)
from .dependencies import get_current_user, require_accountant
from .models import (
    AccountantCreateRequest,
    AccountantResponse,
    AccountantUpdateRequest,
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    TokenPayload,
    TokenResponse,
)
from .security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _build_token_response(
    user_id: int,
    user_type: str,
    role: str,
    name: str,
    email: str,
    conn: Connection,
    client_id: int | None = None,
) -> TokenResponse:
    access_token, expires_in = create_access_token(user_id, user_type, role, client_id)
    refresh_token, expires_at = create_refresh_token(user_id, user_type)
    db_save_refresh_token(conn, refresh_token, user_id, user_type, expires_at)
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user_id=user_id,
        user_name=name,
        user_email=email,
        role=role,
        client_id=client_id,
        refresh_token=refresh_token,
    )


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=TokenResponse, summary="Login de contador ou usuário cliente")
def login(body: LoginRequest, conn: Connection = Depends(lambda: None)):
    """
    Autentica o usuário e retorna access_token + refresh_token.
    O campo `role` deve ser 'accountant' para contadores ou 'client_user'
    para usuários de empresas clientes.
    """
    _unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou senha incorretos.",
    )

    if body.role == "accountant":
        row = db_get_accountant_by_email(conn, body.email)
        if not row or row["status"] != 1:
            raise _unauthorized
        if not verify_password(body.password, row["password_hash"]):
            raise _unauthorized

        return _build_token_response(
            user_id=row["id"],
            user_type="accountant",
            role="accountant",
            name=row["name"],
            email=row["email"],
            conn=conn,
        )

    elif body.role == "client_user":
        row = db_get_client_user_by_email(conn, body.email)
        if not row or row["status"] != 1:
            raise _unauthorized
        if not row.get("password_hash"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Senha não configurada para este usuário. Contate o administrador.",
            )
        if not verify_password(body.password, row["password_hash"]):
            raise _unauthorized

        role = "client-admin" if row["is_admin"] else "client-user"
        return _build_token_response(
            user_id=row["id"],
            user_type="client_user",
            role=role,
            name=row["name"],
            email=row["email"],
            conn=conn,
            client_id=row["client_id"],
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campo 'role' deve ser 'accountant' ou 'client_user'.",
        )


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------

@router.post("/refresh", response_model=RefreshResponse, summary="Renova o access token")
def refresh_token(body: RefreshRequest, conn: Connection = Depends(lambda: None)):
    """
    Recebe um refresh_token válido e retorna um novo access_token.
    O refresh_token recebido é revogado e um novo é emitido (rotation).
    """
    _invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido ou expirado.",
    )

    try:
        payload = decode_refresh_token(body.refresh_token)
    except JWTError:
        raise _invalid

    row = db_get_refresh_token(conn, body.refresh_token)
    if not row or row["revoked"]:
        raise _invalid

    expires_at = row["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise _invalid

    db_revoke_refresh_token(conn, body.refresh_token)

    user_id   = payload["user_id"]
    user_type = payload["user_type"]

    if user_type == "accountant":
        user_row = db_get_accountant_by_id(conn, user_id)
        if not user_row or user_row["status"] != 1:
            raise _invalid
        role = "accountant"
        client_id = None
    else:
        from .db import db_get_client_user_by_email
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, is_admin, client_id, status FROM `ClientUsers` WHERE id = %s LIMIT 1",
                (user_id,),
            )
            user_row = cursor.fetchone()
        if not user_row or user_row["status"] != 1:
            raise _invalid
        role = "client-admin" if user_row["is_admin"] else "client-user"
        client_id = user_row["client_id"]

    new_access_token, expires_in = create_access_token(user_id, user_type, role, client_id)
    new_refresh_token, new_expires_at = create_refresh_token(user_id, user_type)
    db_save_refresh_token(conn, new_refresh_token, user_id, user_type, new_expires_at)

    return RefreshResponse(
        access_token=new_access_token,
        expires_in=expires_in,
        refresh_token=new_refresh_token,
    )


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------

@router.post("/logout", status_code=204, summary="Encerra a sessão atual")
def logout(
    body: RefreshRequest,
    current_user: TokenPayload = Depends(get_current_user),
    conn: Connection = Depends(lambda: None),
):
    """Revoga o refresh_token informado, encerrando a sessão."""
    db_revoke_refresh_token(conn, body.refresh_token)


# ---------------------------------------------------------------------------
# POST /auth/logout-all
# ---------------------------------------------------------------------------

@router.post("/logout-all", status_code=204, summary="Encerra todas as sessões do usuário")
def logout_all(
    current_user: TokenPayload = Depends(get_current_user),
    conn: Connection = Depends(lambda: None),
):
    """Revoga todos os refresh_tokens do usuário autenticado."""
    db_revoke_all_user_tokens(conn, current_user.user_id, current_user.user_type)


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

@router.get("/me", response_model=TokenPayload, summary="Retorna dados do usuário autenticado")
def me(current_user: TokenPayload = Depends(get_current_user)):
    return current_user


# ---------------------------------------------------------------------------
# POST /auth/change-password
# ---------------------------------------------------------------------------

@router.post("/change-password", status_code=204, summary="Altera senha do usuário autenticado")
def change_password(
    body: ChangePasswordRequest,
    current_user: TokenPayload = Depends(get_current_user),
    conn: Connection = Depends(lambda: None),
):
    _unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Senha atual incorreta.",
    )

    if current_user.user_type == "accountant":
        row = db_get_accountant_by_id(conn, current_user.user_id)
        if not row or not verify_password(body.current_password, row["password_hash"]):
            raise _unauthorized
        db_update_accountant_password(conn, current_user.user_id, hash_password(body.new_password))
    else:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT password_hash FROM `ClientUsers` WHERE id = %s LIMIT 1",
                (current_user.user_id,),
            )
            row = cursor.fetchone()
        if not row or not verify_password(body.current_password, row["password_hash"] or ""):
            raise _unauthorized
        db_update_client_user_password(conn, current_user.user_id, hash_password(body.new_password))

    db_revoke_all_user_tokens(conn, current_user.user_id, current_user.user_type)


# ---------------------------------------------------------------------------
# CRUD de Accountants (apenas contadores autenticados podem gerenciar)
# ---------------------------------------------------------------------------

@router.get(
    "/accountants",
    response_model=list[AccountantResponse],
    summary="Lista todos os contadores",
)
def list_accountants(
    _: TokenPayload = Depends(require_accountant),
    conn: Connection = Depends(lambda: None),
):
    return db_get_all_accountants(conn)


@router.post(
    "/accountants",
    response_model=AccountantResponse,
    status_code=201,
    summary="Cria um novo contador",
)
def create_accountant(
    body: AccountantCreateRequest,
    # _: TokenPayload = Depends(require_accountant),
    conn: Connection = Depends(lambda: None),
):
    existing = db_get_accountant_by_email(conn, body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um contador com este email.",
        )
    new_id = db_create_accountant(conn, body.name, body.email, hash_password(body.password))
    return db_get_accountant_by_id(conn, new_id)


@router.put(
    "/accountants/{accountant_id}",
    response_model=AccountantResponse,
    summary="Atualiza dados de um contador",
)
def update_accountant(
    accountant_id: int,
    body: AccountantUpdateRequest,
    _: TokenPayload = Depends(require_accountant),
    conn: Connection = Depends(lambda: None),
):
    row = db_get_accountant_by_id(conn, accountant_id)
    if not row:
        raise HTTPException(status_code=404, detail="Contador não encontrado.")
    db_update_accountant(conn, accountant_id, body.name, body.email)
    return db_get_accountant_by_id(conn, accountant_id)


@router.delete(
    "/accountants/{accountant_id}",
    status_code=204,
    summary="Remove um contador (soft delete)",
)
def delete_accountant(
    accountant_id: int,
    current_user: TokenPayload = Depends(require_accountant),
    conn: Connection = Depends(lambda: None),
):
    if current_user.user_id == accountant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode remover sua própria conta.",
        )
    row = db_get_accountant_by_id(conn, accountant_id)
    if not row:
        raise HTTPException(status_code=404, detail="Contador não encontrado.")
    db_delete_accountant(conn, accountant_id)


# ---------------------------------------------------------------------------
# POST /auth/admin/set-client-user-password
# ---------------------------------------------------------------------------

@router.post(
    "/admin/set-client-user-password",
    status_code=204,
    summary="Contador define senha inicial de um usuário cliente",
)
def set_client_user_password(
    user_id: int,
    new_password: str,
    _: TokenPayload = Depends(require_accountant),
    conn: Connection = Depends(lambda: None),
):
    """
    Permite que um contador defina ou redefina a senha de um ClientUser.
    Útil para o primeiro acesso ou para reset administrativo.
    """
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM `ClientUsers` WHERE id = %s AND status = 1 LIMIT 1",
            (user_id,),
        )
        row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    db_update_client_user_password(conn, user_id, hash_password(new_password))
    db_revoke_all_user_tokens(conn, user_id, "client_user")
