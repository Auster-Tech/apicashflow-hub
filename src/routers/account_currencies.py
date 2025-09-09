from fastapi import APIRouter
from test.functions import * 
from test.database import *

router = APIRouter()

# --- Account Currency CRUD Endpoints ---
@router.get("/", response_model=List[AccountCurrency], tags=["Account Configuration"])
def get_account_currencies(): return db_account_currencies

@router.post("/", response_model=AccountCurrency, status_code=201, tags=["Account Configuration"])
def create_account_currency(currency: AccountCurrency):
    if any(c.code.lower() == currency.code.lower() for c in db_account_currencies):
        raise HTTPException(409, f"Currency '{currency.code}' already exists.")
    db_account_currencies.append(currency)
    return currency