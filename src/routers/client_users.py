from fastapi import APIRouter
from test.functions import * 
from test.database import *

router = APIRouter()
# --- Client User CRUD Endpoints ---
@router.get("/", response_model=List[CompanyUser], tags=["Client Users"])
def get_client_users(client_id: int): return find_client_or_404(client_id).users

@router.post("/", response_model=CompanyUser, status_code=201, tags=["Client Users"])
def add_user_to_client(client_id: int, new_user: CompanyUser):
    client = find_client_or_404(client_id)
    if find_user_by_email(client, new_user.email):
        raise HTTPException(409, f"User with email '{new_user.email}' already exists.")
    client.users.append(new_user)
    return new_user

@router.put("/{user_email}", response_model=CompanyUser, tags=["Client Users"])
def update_client_user(client_id: int, user_email: EmailStr, user_update: CompanyUser):
    client = find_client_or_404(client_id)
    user_info = find_user_by_email(client, user_email)
    if not user_info: raise HTTPException(404, f"User with email '{user_email}' not found.")
    user_index, old_user = user_info
    if old_user.is_admin and len([u for u in client.users if u.is_admin]) == 1 and not user_update.is_admin:
        raise HTTPException(400, "Cannot remove the last administrator.")
    client.users[user_index] = user_update
    return user_update

@router.delete("/{user_email}", status_code=204, tags=["Client Users"])
def delete_client_user(client_id: int, user_email: EmailStr):
    client = find_client_or_404(client_id)
    user_info = find_user_by_email(client, user_email)
    if not user_info: raise HTTPException(404, f"User with email '{user_email}' not found.")
    user_index, user_to_delete = user_info
    if len(client.users) <= 1: raise HTTPException(400, "Cannot delete the last user.")
    if user_to_delete.is_admin and len([u for u in client.users if u.is_admin]) <= 1:
        raise HTTPException(400, "Cannot delete the last administrator.")
    del client.users[user_index]
    return None