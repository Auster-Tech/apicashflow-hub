from datetime import datetime, timezone
from typing import Optional

from pymysql.connections import Connection


# ---------------------------------------------------------------------------
# Accountant
# ---------------------------------------------------------------------------

def db_get_accountant_by_email(conn: Connection, email: str) -> Optional[dict]:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, email, password_hash, status FROM `Accountant` WHERE email = %s LIMIT 1",
            (email,),
        )
        return cursor.fetchone()


def db_get_accountant_by_id(conn: Connection, accountant_id: int) -> Optional[dict]:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, email, password_hash, status FROM `Accountant` WHERE id = %s LIMIT 1",
            (accountant_id,),
        )
        return cursor.fetchone()


def db_get_all_accountants(conn: Connection) -> list[dict]:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, email, status FROM `Accountant` WHERE status != 99 ORDER BY name"
        )
        return cursor.fetchall()


def db_create_accountant(conn: Connection, name: str, email: str, password_hash: str) -> int:
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO `Accountant` (name, email, password_hash, status) VALUES (%s, %s, %s, 1)",
            (name, email, password_hash),
        )
        last_id = cursor.lastrowid
    conn.commit()
    return last_id


def db_update_accountant(conn: Connection, accountant_id: int, name: str, email: str) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE `Accountant` SET name = %s, email = %s WHERE id = %s",
            (name, email, accountant_id),
        )
    conn.commit()


def db_update_accountant_password(conn: Connection, accountant_id: int, password_hash: str) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE `Accountant` SET password_hash = %s WHERE id = %s",
            (password_hash, accountant_id),
        )
    conn.commit()


def db_delete_accountant(conn: Connection, accountant_id: int) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE `Accountant` SET status = 99 WHERE id = %s",
            (accountant_id,),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# ClientUser password
# ---------------------------------------------------------------------------

def db_get_client_user_by_email(conn: Connection, email: str) -> Optional[dict]:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, email, password_hash, is_admin, client_id, status FROM `ClientUsers` WHERE email = %s AND status = 1 LIMIT 1",
            (email,),
        )
        return cursor.fetchone()


def db_update_client_user_password(conn: Connection, user_id: int, password_hash: str) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE `ClientUsers` SET password_hash = %s WHERE id = %s",
            (password_hash, user_id),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# RefreshToken
# ---------------------------------------------------------------------------

def db_save_refresh_token(
    conn: Connection,
    token: str,
    user_id: int,
    user_type: str,
    expires_at: datetime,
) -> None:
    expires_at_naive = expires_at.replace(tzinfo=None) if expires_at.tzinfo else expires_at
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO `RefreshToken` (token, user_id, user_type, expires_at, revoked) VALUES (%s, %s, %s, %s, 0)",
            (token, user_id, user_type, expires_at_naive),
        )
    conn.commit()


def db_get_refresh_token(conn: Connection, token: str) -> Optional[dict]:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, token, user_id, user_type, expires_at, revoked FROM `RefreshToken` WHERE token = %s LIMIT 1",
            (token,),
        )
        return cursor.fetchone()


def db_revoke_refresh_token(conn: Connection, token: str) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE `RefreshToken` SET revoked = 1 WHERE token = %s",
            (token,),
        )
    conn.commit()


def db_revoke_all_user_tokens(conn: Connection, user_id: int, user_type: str) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE `RefreshToken` SET revoked = 1 WHERE user_id = %s AND user_type = %s",
            (user_id, user_type),
        )
    conn.commit()


def db_cleanup_expired_tokens(conn: Connection) -> None:
    """Remove tokens expirados há mais de 1 dia. Chamar periodicamente."""
    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM `RefreshToken` WHERE expires_at < (NOW() - INTERVAL 1 DAY)"
        )
    conn.commit()
