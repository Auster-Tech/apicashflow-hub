from pydantic import BaseModel, EmailStr
from typing import Optional


# --- Request models ---

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # 'accountant' | 'client_user'


class RefreshRequest(BaseModel):
    refresh_token: str


class AccountantCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class AccountantUpdateRequest(BaseModel):
    name: str
    email: EmailStr


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# --- Response models ---

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user_id: int
    user_name: str
    user_email: str
    role: str
    client_id: Optional[int] = None


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AccountantResponse(BaseModel):
    id: int
    name: str
    email: str
    status: int


# --- Internal token payload ---

class TokenPayload(BaseModel):
    sub: str          # "<user_type>:<user_id>"
    user_id: int
    user_type: str    # 'accountant' | 'client_user'
    role: str         # 'accountant' | 'client-admin' | 'client-user'
    client_id: Optional[int] = None
    exp: int
