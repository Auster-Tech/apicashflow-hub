from fastapi import APIRouter
from test.functions import * 
from test.database import *

router = APIRouter()

# --- Account Type CRUD Endpoints ---
@router.get("/", response_model=List[AccountType], tags=["Account Configuration"])
def get_account_types(): return db_account_types

@router.post("/", response_model=AccountType, status_code=201, tags=["Account Configuration"])
def create_account_type(acc_type: AccountType):
    if any(t.name.lower() == acc_type.name.lower() for t in db_account_types):
        raise HTTPException(409, f"Account type '{acc_type.name}' already exists.")
    db_account_types.append(acc_type)
    return acc_type