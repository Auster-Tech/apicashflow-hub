from fastapi import APIRouter
from test.functions import * 
from test.database import *

router = APIRouter()

# --- Financial Account CRUD Endpoints ---
@router.post("/", response_model=FinancialAccountResponse, status_code=201, tags=["Financial Accounts"])
def create_financial_account(client_id: int, account_data: FinancialAccountCreate):
    global account_id_counter
    find_client_or_404(client_id) # Ensure client exists
    find_account_type_or_404(account_data.account_type) # Validate type
    find_currency_or_404(account_data.account_currency) # Validate currency
    
    new_account = FinancialAccountResponse(account_id=account_id_counter, **account_data.dict())
    db_financial_accounts[client_id].append(new_account)
    account_id_counter += 1
    return new_account

@router.get("/", response_model=List[FinancialAccountResponse], tags=["Financial Accounts"])
def get_all_financial_accounts_for_client(client_id: int):
    find_client_or_404(client_id)
    return db_financial_accounts.get(client_id, [])

@router.get("/{account_id}", response_model=FinancialAccountResponse, tags=["Financial Accounts"])
def get_financial_account(client_id: int, account_id: int):
    return find_financial_account_or_404(client_id, account_id)

@router.put("/{account_id}", response_model=FinancialAccountResponse, tags=["Financial Accounts"])
def update_financial_account(client_id: int, account_id: int, account_data: FinancialAccountCreate):
    find_client_or_404(client_id)
    find_account_type_or_404(account_data.account_type)
    find_currency_or_404(account_data.account_currency)
    
    account_to_update = find_financial_account_or_404(client_id, account_id)
    account_index = db_financial_accounts[client_id].index(account_to_update)
    
    updated_account = FinancialAccountResponse(account_id=account_id, **account_data.dict())
    db_financial_accounts[client_id][account_index] = updated_account
    return updated_account

@router.delete("/{account_id}", status_code=204, tags=["Financial Accounts"])
def delete_financial_account(client_id: int, account_id: int):
    account_to_delete = find_financial_account_or_404(client_id, account_id)
    db_financial_accounts[client_id].remove(account_to_delete)
    return None