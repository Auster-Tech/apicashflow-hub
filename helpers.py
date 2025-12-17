from fastapi import FastAPI, HTTPException, status, Path
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum
from models import *
from pymysql.connections import Connection

# --- Generic Helper Functions ---
def find_item_by_id(item_id: int, db_list: list, item_name: str, connection: Connection):
    for item in db_list:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"{item_name} with ID {item_id} not found")

# --- Specific Helper Functions ---
def find_user_by_email(client: ClientResponse, email: EmailStr, connection: Connection):
    for i, user in enumerate(client.users):
        if user.email == email: return i, user
    return None

def find_account_type_or_404(name: str, connection: Connection):
    for acc_type in db_account_types:
        if acc_type.name.lower() == name.lower(): return acc_type
    raise HTTPException(status_code=404, detail=f"Account type '{name}' not found.")

def find_currency_or_404(code: str, connection: Connection):
    for currency in db_account_currencies:
        if currency.code.lower() == code.lower(): return currency
    raise HTTPException(status_code=404, detail=f"Currency code '{code}' not found.")

def find_client_or_404(client_id: int, connection: Connection):
    for client in db_clients:
        if client.client_id == client_id: return client
    raise HTTPException(status_code=404, detail=f"Client with ID {client_id} not found")

def find_financial_account_or_404(client_id: int, account_id: int, connection: Connection):
    if client_id not in db_financial_accounts:
        raise HTTPException(status_code=404, detail=f"No accounts found for client {client_id}")
    for account in db_financial_accounts[client_id]:
        if account.account_id == account_id: return account
    raise HTTPException(status_code=404, detail=f"Account with ID {account_id} not found for client {client_id}")

def find_transaction_or_404(client_id: int, transaction_id: int, connection: Connection):
    if client_id not in db_transactions:
        raise HTTPException(status_code=404, detail=f"No transactions found for client {client_id}")
    for tx in db_transactions[client_id]:
        if tx.id == transaction_id: return tx
    raise HTTPException(status_code=404, detail=f"Transaction with ID {transaction_id} not found for client {client_id}")

def update_account_balance(account: FinancialAccountResponse, category: Category, amount: Decimal, operation: str, connection: Connection):
    """Updates account balance. 'add' for new, 'subtract' for deletion/old value."""
    multiplier = -1 if category.type == CategoryType.EXPENSE else 1
    if operation == 'subtract':
        account.balance -= (amount * multiplier)
    else: # add
        account.balance += (amount * multiplier)

def create_client(connection: Connection):
    with connection:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `ZTest` (`col`) VALUES (%s), (%s), (%s)"
            cursor.execute(sql, [('webmaster',),('python',),('org',)])

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `ZTest` WHERE `col`=%s"
            cursor.execute(sql, ('webmaster@python.org',))
            result = cursor.fetchone()
            print(result)