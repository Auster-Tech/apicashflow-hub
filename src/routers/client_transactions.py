from typing import List
from fastapi import APIRouter
from models import TransactionResponse, TransactionCreate
from test.functions import * 
from test.database import *

router = APIRouter()

# --- Transaction CRUD Endpoints ---
@router.post("/", response_model=TransactionResponse, status_code=201, tags=["Transactions"])
def create_transaction(client_id: int, tx_data: TransactionCreate):
    global transaction_id_counter
    find_client_or_404(client_id)
    account = find_financial_account_or_404(client_id, tx_data.financial_account_id)
    category = find_item_by_id(tx_data.category_id, db_categories, "Category")
    find_item_by_id(tx_data.status_id, db_statuses, "Status") # Validate status
    
    new_tx = TransactionResponse(id=transaction_id_counter, **tx_data.dict())
    db_transactions[client_id].append(new_tx)
    transaction_id_counter += 1
    
    # Update account balance
    update_account_balance(account, category, new_tx.amount, 'add')
    
    return new_tx

@router.get("/", response_model=List[TransactionResponse], tags=["Transactions"])
def get_all_transactions(client_id: int):
    find_client_or_404(client_id)
    return db_transactions.get(client_id, [])

@router.get("/{transaction_id}", response_model=TransactionResponse, tags=["Transactions"])
def get_transaction(client_id: int, transaction_id: int):
    return find_transaction_or_404(client_id, transaction_id)

@router.put("/{transaction_id}", response_model=TransactionResponse, tags=["Transactions"])
def update_transaction(client_id: int, transaction_id: int, tx_data: TransactionCreate):
    find_client_or_404(client_id)
    old_tx = find_transaction_or_404(client_id, transaction_id)
    
    # --- Revert old transaction's effect on balance ---
    old_account = find_financial_account_or_404(client_id, old_tx.financial_account_id)
    old_category = find_item_by_id(old_tx.category_id, db_categories, "Category")
    update_account_balance(old_account, old_category, old_tx.amount, 'subtract')

    # --- Apply new transaction's effect on balance ---
    new_account = find_financial_account_or_404(client_id, tx_data.financial_account_id)
    new_category = find_item_by_id(tx_data.category_id, db_categories, "Category")
    update_account_balance(new_account, new_category, tx_data.amount, 'add')
    
    # --- Update the transaction data ---
    tx_index = db_transactions[client_id].index(old_tx)
    updated_tx = TransactionResponse(id=transaction_id, **tx_data.dict())
    db_transactions[client_id][tx_index] = updated_tx
    
    return updated_tx

@router.delete("/{transaction_id}", status_code=204, tags=["Transactions"])
def delete_transaction(client_id: int, transaction_id: int):
    find_client_or_404(client_id)
    tx_to_delete = find_transaction_or_404(client_id, transaction_id)
    
    # Revert the transaction's effect on the account balance
    account = find_financial_account_or_404(client_id, tx_to_delete.financial_account_id)
    category = find_item_by_id(tx_to_delete.category_id, db_categories, "Category")
    update_account_balance(account, category, tx_to_delete.amount, 'subtract')
    
    db_transactions[client_id].remove(tx_to_delete)
    return None