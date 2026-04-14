from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from pymysql.connections import Connection

from .db import (
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
# Sentinela de banco de dados
# ---------------------------------------------------------------------------
# Função nomeada usada como placeholder de Depends() em todas as rotas deste
# router. O main.py faz app.dependency_overrides[get_auth_db] = get_db,
# substituindo-a pela função real do pool de conexões.

def get_auth_db():  # pragma: no cover
    raise RuntimeError("get_auth_db nao foi sobrescrito via dependency_overrides")


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

@router.post("/login", response_model=TokenResponse, summary="Login de contador ou usuario cliente")
def login(body: LoginRequest, conn: Connection = Depends(get_auth_db)):
    """
    Autentica o usuario e retorna access_token + refresh_token.
    O campo `role` deve ser 'accountant' para contadores ou 'client_user'
    para usuarios de empresas clientes.
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
                detail="Senha nao configurada para este usuario. Contate o administrador.",
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
def refresh_token(body: RefreshRequest, conn: Connection = Depends(get_auth_db)):
    """
    Recebe um refresh_token valido e retorna um novo access_token.
    O refresh_token recebido e revogado e um novo e emitido (rotation).
    """
    _invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token invalido ou expirado.",
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

@router.post("/logout", status_code=204, summary="Encerra a sessao atual")
def logout(
    body: RefreshRequest,
    current_user: TokenPayload = Depends(get_current_user),
    conn: Connection = Depends(get_auth_db),
):
    """Revoga o refresh_token informado, encerrando a sessao."""
    db_revoke_refresh_token(conn, body.refresh_token)


# ---------------------------------------------------------------------------
# POST /auth/logout-all
# ---------------------------------------------------------------------------

@router.post("/logout-all", status_code=204, summary="Encerra todas as sessoes do usuario")
def logout_all(
    current_user: TokenPayload = Depends(get_current_user),
    conn: Connection = Depends(get_auth_db),
):
    """Revoga todos os refresh_tokens do usuario autenticado."""
    db_revoke_all_user_tokens(conn, current_user.user_id, current_user.user_type)


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

@router.get("/me", response_model=TokenPayload, summary="Retorna dados do usuario autenticado")
def me(current_user: TokenPayload = Depends(get_current_user)):
    return current_user


# ---------------------------------------------------------------------------
# POST /auth/change-password
# ---------------------------------------------------------------------------

@router.post("/change-password", status_code=204, summary="Altera senha do usuario autenticado")
def change_password(
    body: ChangePasswordRequest,
    current_user: TokenPayload = Depends(get_current_user),
    conn: Connection = Depends(get_auth_db),
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
    conn: Connection = Depends(get_auth_db),
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
    _: TokenPayload = Depends(require_accountant),
    conn: Connection = Depends(get_auth_db),
):
    existing = db_get_accountant_by_email(conn, body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ja existe um contador com este email.",
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
    conn: Connection = Depends(get_auth_db),
):
    row = db_get_accountant_by_id(conn, accountant_id)
    if not row:
        raise HTTPException(status_code=404, detail="Contador nao encontrado.")
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
    conn: Connection = Depends(get_auth_db),
):
    if current_user.user_id == accountant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voce nao pode remover sua propria conta.",
        )
    row = db_get_accountant_by_id(conn, accountant_id)
    if not row:
        raise HTTPException(status_code=404, detail="Contador nao encontrado.")
    db_delete_accountant(conn, accountant_id)


# ---------------------------------------------------------------------------
# POST /auth/admin/set-client-user-password
# ---------------------------------------------------------------------------

@router.post(
    "/admin/set-client-user-password",
    status_code=204,
    summary="Contador define senha inicial de um usuario cliente",
)
def set_client_user_password(
    user_id: int,
    new_password: str,
    _: TokenPayload = Depends(require_accountant),
    conn: Connection = Depends(get_auth_db),
):
    """
    Permite que um contador defina ou redefina a senha de um ClientUser.
    Util para o primeiro acesso ou para reset administrativo.
    """
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM `ClientUsers` WHERE id = %s AND status = 1 LIMIT 1",
            (user_id,),
        )
        row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado.")

    db_update_client_user_password(conn, user_id, hash_password(new_password))
    db_revoke_all_user_tokens(conn, user_id, "client_user")
