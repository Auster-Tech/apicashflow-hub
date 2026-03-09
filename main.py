# main.py
#
# --- Project Setup ---
# 1. Save this code as 'main.py'.
# 2. Create a file named 'requirements.txt' in the same directory with the following content:
#    fastapi
#    uvicorn[standard]
#    pydantic[email]
#
# 3. Open your terminal or command prompt in that directory.
# 4. Create a virtual environment (recommended):
#    python -m venv venv
#    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
#
# 5. Install the required libraries:
#    pip install -r requirements.txt
#
# 6. Run the development server:
#    uvicorn main:app --reload
#
# 7. Open your browser and go to http://127.0.0.1:8000/docs to see the interactive API documentation.

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Path
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum
from models import *
import helpers
import pymysql.cursors
from pymysql.connections import Connection
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Database Connection ---
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DATABASE = os.getenv("DB_DATABASE")

    connection: Connection = pymysql.connect(host=DB_HOST,
                                user=DB_USER,
                                password=DB_PASSWORD,
                                database=DB_DATABASE,
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    app.state.connection = connection

    yield

    app.state.connection.close()

    return

# --- Initialize FastAPI App ---
app = FastAPI(
    title="Accounting Control API",
    description="An API for accountants to manage their clients' financial data.",
    version="1.0.0",
    lifespan=lifespan
)


# --- API Endpoints ---
@app.get("/")
def read_root(): return {"message": "Welcome to the Accounting Control API!"}

# --- Client CRUD Endpoints ---
@app.post("/clients/", response_model=ClientResponse, status_code=201, tags=["Clients"])
def create_client(client_data: ClientCreate):
    try:
        new_client: ClientResponse = helpers.ClientHelper.create(app.state.connection, client_data)
        return new_client
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.get("/clients/", response_model=List[ClientResponse], tags=["Clients"])
def get_all_clients():
    try:
        client_list: List[ClientResponse] = helpers.ClientHelper.find_all(app.state.connection)
        return client_list
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.get("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
def get_client_by_id(client_id: int):
    try:
        client: ClientResponse = helpers.ClientHelper.find_first_by_field(app.state.connection, 
                                                                         "id", 
                                                                         client_id)
        return client
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.put("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
def update_client(client_id: int, client_data: ClientCreate):
    try:
        client: ClientResponse = helpers.ClientHelper.update(app.state.connection, 
                                                        client_id, 
                                                        client_data)
        return client
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/clients/{client_id}", status_code=204, tags=["Clients"])
def delete_client(client_id: int):
    try:
        helpers.ClientHelper.delete(app.state.connection, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

# --- Client User CRUD Endpoints ---
@app.get("/clients/{client_id}/users/", response_model=List[CompanyUser], tags=["Client Users"])
def get_client_users(client_id: int):
    try:
        users_list: List[CompanyUser] = helpers.CompanyUserHelper.find_all(app.state.connection, client_id)
        return users_list
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.get("/clients/{client_id}/users/{user_id}", response_model=List[CompanyUser], tags=["Client Users"])
def get_client_user_by_id(client_id: int, user_id: int):
    try:
        user: CompanyUser = helpers.CompanyUserHelper.find_first_by_field(app.state.connection, 
                                                                         user_id, 
                                                                         client_id)
        return user
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/clients/{client_id}/users/", response_model=CompanyUser, status_code=201, tags=["Client Users"])
def add_user_to_client(client_id: int, new_user: CompanyUser):
    try:
        new_user: CompanyUser = helpers.CompanyUserHelper.create(app.state.connection, new_user, client_id)
        return new_user
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/clients/{client_id}/users/{user_id}", response_model=CompanyUser, tags=["Client Users"])
def update_client_user(client_id: int, user_id: int, user_update: CompanyUser):
    try:
        new_user: CompanyUser = helpers.CompanyUserHelper.update(app.state.connection, 
                                                                 user_id, 
                                                                 user_update, 
                                                                 client_id)
        return new_user
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/clients/{client_id}/users/{user_id}", status_code=204, tags=["Client Users"])
def delete_client_user(client_id: int, user_id: int):
    try:
        helpers.CompanyUserHelper.delete(app.state.connection, user_id, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

# --- Account Type CRUD Endpoints ---
@app.get("/account-types/", response_model=List[AccountType], tags=["Account Configuration"])
def get_account_types():
    try:
        account: AccountType = helpers.AccountTypeHelper.find_all(app.state.connection)
        return account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/account-types/", response_model=AccountType, status_code=201, tags=["Account Configuration"])
def create_account_type(acc_type: AccountType):
    try:
        new_acc: AccountType = helpers.AccountTypeHelper.create(app.state.connection, acc_type)
        return new_acc
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/account-types/{account_id}", response_model=AccountType, tags=["Account Configuration"])
def update_account_type(account_id: int, acc_update: AccountType):
    try:
        new_acc: AccountType = helpers.AccountTypeHelper.update(app.state.connection, 
                                                                 account_id, 
                                                                 acc_update)
        return new_acc
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/account-types/{account_id}", status_code=204, tags=["Account Configuration"])
def delete_account_type(account_id: int):
    try:
        helpers.AccountTypeHelper.delete(app.state.connection, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

# --- Account Currency CRUD Endpoints ---
@app.get("/account-currencies/", response_model=List[AccountCurrency], tags=["Account Configuration"])
def get_account_currencies():
    try:
        account: AccountCurrency = helpers.AccountCurrencyHelper.find_all(app.state.connection)
        return account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/account-currencies/", response_model=AccountCurrency, status_code=201, tags=["Account Configuration"])
def create_account_currencies(acc: AccountCurrency):
    try:
        new_acc: AccountCurrency = helpers.AccountCurrencyHelper.create(app.state.connection, acc)
        return new_acc
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/account-currencies/{account_id}", response_model=AccountCurrency, tags=["Account Configuration"])
def update_account_currencies(account_id: int, acc_update: AccountCurrency):
    try:
        new_acc: AccountCurrency = helpers.AccountCurrencyHelper.update(app.state.connection, 
                                                                 account_id, 
                                                                 acc_update)
        return new_acc
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/account-currencies/{account_id}", status_code=204, tags=["Account Configuration"])
def delete_account_currencies(account_id: int):
    try:
        helpers.AccountCurrencyHelper.delete(app.state.connection, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
# --- Account Balance CRUD Endpoints ---
@app.get("/account-balance/", response_model=List[AccountBalance], tags=["Account Configuration"])
def get_every_account_balance():
    try:
        balance: AccountBalance = helpers.AccountBalanceHelper.find_all(app.state.connection)
        return balance
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.get("/account-balance/{account_id}", response_model=List[AccountBalance], tags=["Account Configuration"])
def get_account_balances_from_account(account_id: int):
    try:
        balance: AccountBalance = helpers.AccountBalanceHelper.find_all_by_account(app.state.connection, account_id)
        return balance
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.get("/account-balance/{account_id}/{balance_id}", response_model=List[AccountBalance], tags=["Account Configuration"])
def get_account_balance(account_id: int, balance_id: int):
    try:
        balance: AccountBalance = helpers.AccountBalanceHelper.find_first_by_id(app.state.connection, balance_id=balance_id, account_id=account_id)
        return balance
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/account-balance/{account_id}", status_code=201, tags=["Account Configuration"])
def create_account_balance(balance: AccountBalance, account_id: int):
    try:
        helpers.AccountBalanceHelper.create(app.state.connection, balance, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/account-balance/{account_id}/{balance_id}", response_model=AccountBalance, tags=["Account Configuration"])
def update_account_balance(balance_id: int, account_id: int, balance: AccountBalance):
    try:
        new_balance: AccountBalance = helpers.AccountBalanceHelper.update(app.state.connection, 
                                                                          balance_id,
                                                                          balance,
                                                                          account_id)
        return new_balance
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/account-balance/{account_id}/{balance_id}", status_code=204, tags=["Account Configuration"])
def delete_account_balance(balance_id: int, account_id: int):
    try:
        helpers.AccountBalanceHelper.delete(app.state.connection, balance_id, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

# --- Financial Account CRUD Endpoints ---
@app.post("/clients/{client_id}/accounts/", response_model=Account, status_code=201, tags=["Financial Accounts"])
def create_financial_account(client_id: int, account_data: Account):
    try:
        new_account: Account = helpers.AccountHelper.create(app.state.connection, account_data, client_id)
        return new_account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.get("/clients/{client_id}/accounts/", response_model=List[Account], tags=["Financial Accounts"])
def get_all_financial_accounts_for_client(client_id: int):
    try:
        account: Account = helpers.AccountHelper.find_all(app.state.connection, client_id)
        return account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.get("/clients/{client_id}/accounts/{account_id}", response_model=Account, tags=["Financial Accounts"])
def get_financial_account(client_id: int, account_id: int):
    try:
        account: Account = helpers.AccountHelper.find_first_by_id(app.state.connection, 
                                                                         account_id, 
                                                                         client_id)
        return account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/clients/{client_id}/accounts/{account_id}", response_model=Account, tags=["Financial Accounts"])
def update_financial_account(client_id: int, account_id: int, account_data: Account):
    try:
        new_account: Account = helpers.AccountHelper.update(app.state.connection, 
                                                                 account_id, 
                                                                 account_data, 
                                                                 client_id)
        return new_account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/clients/{client_id}/accounts/{account_id}", status_code=204, tags=["Financial Accounts"])
def delete_financial_account(client_id: int, account_id: int):
    try:
        helpers.CompanyUserHelper.delete(app.state.connection, account_id, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

# --- Transaction Status CRUD Endpoints ---
@app.get("/transaction-status/", response_model=List[TransactionStatus], tags=["Transaction Status"])
def get_transaction_status():
    try:
        transaction_status: TransactionStatus = helpers.TransactionStatusHelper.find_all(app.state.connection)
        return transaction_status
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/transaction-status/", response_model=TransactionStatus, status_code=201, tags=["Transaction Status"])
def create_transaction_status(transaction_status: TransactionStatus):
    try:
        new_transaction_status: TransactionStatus = helpers.TransactionStatusHelper.create(app.state.connection, transaction_status)
        return new_transaction_status
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/transaction-status/{transaction_id}", response_model=TransactionStatus, tags=["Transaction Status"])
def update_transaction_status(transaction_id: int, transaction_status_update: TransactionStatus):
    try:
        new_transaction_status: TransactionStatus = helpers.TransactionStatusHelper.update(app.state.connection, 
                                                                 transaction_id, 
                                                                 transaction_status_update)
        return new_transaction_status
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/transaction-status/{transaction_id}", status_code=204, tags=["Transaction Status"])
def delete_transaction_status(transaction_id: int):
    try:
        helpers.TransactionStatusHelper.delete(app.state.connection, transaction_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
# --- Invoice CRUD Endpoints ---
@app.get("/invoice/", response_model=List[Invoice], tags=["Invoice"])
def get_invoice():
    try:
        invoice: Invoice = helpers.InvoiceHelper.find_all(app.state.connection)
        return invoice
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/invoice/", response_model=Invoice, status_code=201, tags=["Invoice"])
def create_invoice(invoice: Invoice):
    try:
        new_invoice: Invoice = helpers.InvoiceHelper.create(app.state.connection, invoice)
        return new_invoice
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/invoice/{invoice_id}", response_model=Invoice, tags=["Invoice"])
def update_invoice(invoice_id: int, invoice_update: Invoice):
    try:
        new_invoice: Invoice = helpers.InvoiceHelper.update(app.state.connection, 
                                                                 invoice_id, 
                                                                 invoice_update)
        return new_invoice
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/invoice/{invoice_id}", status_code=204, tags=["Invoice"])
def delete_invoice(invoice_id: int):
    try:
        helpers.InvoiceHelper.delete(app.state.connection, invoice_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
# --- Partner CRUD Endpoints ---
@app.get("/partner/", response_model=List[Partner], tags=["Partner"])
def get_partner():
    try:
        partner: Partner = helpers.PartnerHelper.find_all(app.state.connection)
        return partner
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/partner/", status_code=201, tags=["Partner"])
def create_partner(partner: Partner):
    try:
        helpers.PartnerHelper.create(app.state.connection, partner)
        
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/partner/{partner_id}", response_model=Partner, tags=["Partner"])
def update_partner(partner_id: int, partner_update: Partner):
    try:
        new_partner: Partner = helpers.PartnerHelper.update(app.state.connection, 
                                                                 partner_id, 
                                                                 partner_update)
        return new_partner
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/partner/{partner_id}", status_code=204, tags=["Partner"])
def delete_partner(partner_id: int):
    try:
        helpers.PartnerHelper.delete(app.state.connection, partner_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
# --- Category CRUD Endpoints ---
@app.get("/category/", response_model=List[Category], tags=["Category"])
def get_category():
    try:
        category: Category = helpers.CategoryHelper.find_all(app.state.connection)
        return category
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/category/", response_model=Category, status_code=201, tags=["Category"])
def create_category(category: Category):
    try:
        new_category: Category = helpers.CategoryHelper.create(app.state.connection, category)
        return new_category
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/category/{category_id}", response_model=Category, tags=["Category"])
def update_category(category_id: int, category_update: Category):
    try:
        new_category: Category = helpers.CategoryHelper.update(app.state.connection, 
                                                                 category_id, 
                                                                 category_update)
        return new_category
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/category/{category_id}", status_code=204, tags=["Category"])
def delete_category(category_id: int):
    try:
        helpers.CategoryHelper.delete(app.state.connection, category_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
# --- Cost Center CRUD Endpoints ---
@app.get("/cost-center/", response_model=List[CostCenter], tags=["Cost Center"])
def get_cost_center():
    try:
        cost_center: CostCenter = helpers.CostCenterHelper.find_all(app.state.connection)
        return cost_center
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/cost-center/", response_model=CostCenter, status_code=201, tags=["Cost Center"])
def create_cost_center(cost_center: CostCenter):
    try:
        new_cost_center: CostCenter = helpers.CostCenterHelper.create(app.state.connection, cost_center)
        return new_cost_center
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/cost-center/{cost_center_id}", response_model=CostCenter, tags=["Cost Center"])
def update_cost_center(cost_center_id: int, cost_center_update: CostCenter):
    try:
        new_cost_center: CostCenter = helpers.CostCenterHelper.update(app.state.connection, 
                                                                 cost_center_id, 
                                                                 cost_center_update)
        return new_cost_center
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/cost-center/{cost_center_id}", status_code=204, tags=["Cost Center"])
def delete_cost_center(cost_center_id: int):
    try:
        helpers.CostCenterHelper.delete(app.state.connection, cost_center_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# --- Transactions CRUD Endpoints ---
@app.get("/transactions/", response_model=List[Transaction], tags=["Transactions"])
def get_every_account_transaction():
    try:
        transaction_list: List[Transaction] = helpers.TransactionHelper.find_all(app.state.connection)
        return transaction_list
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.get("/transactions/{account_id}", response_model=List[Transaction], tags=["Transactions"])
def get_account_transactions_from_account(account_id: int):
    try:
        transaction_list: List[Transaction] = helpers.TransactionHelper.find_all_by_account(app.state.connection, account_id)
        return transaction_list
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.get("/transactions/{account_id}/{transaction_id}", response_model=List[Transaction], tags=["Transactions"])
def get_account_transaction(account_id: int, transaction_id: int):
    try:
        transaction: Transaction = helpers.TransactionHelper.find_first_by_id(app.state.connection, transaction_id=transaction_id, account_id=account_id)
        return transaction
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/transactions/{account_id}", status_code=201, tags=["Transactions"])
def create_account_transaction(transaction: Transaction, account_id: int):
    try:
        helpers.TransactionHelper.create(app.state.connection, transaction, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/transactions/{account_id}/{transaction_id}", response_model=Transaction, tags=["Transactions"])
def update_account_transaction(transaction_id: int, account_id: int, transaction: Transaction):
    try:
        new_transaction: Transaction = helpers.TransactionHelper.update(app.state.connection, 
                                                                          transaction_id,
                                                                          transaction,
                                                                          account_id)
        return new_transaction
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/transactions/{account_id}/{transaction_id}", status_code=204, tags=["Transactions"])
def delete_account_transaction(transaction_id: int, account_id: int):
    try:
        helpers.TransactionHelper.delete(app.state.connection, transaction_id, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))