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
import logging
from fastapi import Depends, FastAPI, HTTPException, status, Path
from fastapi.middleware.cors import CORSMiddleware
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
from dbutils.pooled_db import PooledDB

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=2,
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    yield

def get_db():
    conn = app.state.pool.connection()
    try:
        yield conn
    finally:
        conn.close()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# --- Initialize FastAPI App ---
app = FastAPI(
    title="Accounting Control API",
    description="An API for accountants to manage their clients' financial data.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://localhost:8080"],  # origem do seu React
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],      # GET, POST, PUT, DELETE, etc.
    allow_headers=["Authorization", "Content-Type"],      # Authorization, Content-Type, etc.
)

# --- API Endpoints ---
@app.get("/")
def read_root(): return {"message": "Welcome to the Accounting Control API!"}

# --- Client CRUD Endpoints ---
@app.get("/clients/", response_model=List[ClientResponse], tags=["Clients"])
def get_all_clients(conn=Depends(get_db)):
    try:
        client_list: List[ClientResponse] = helpers.ClientHelper.find_all(conn)
        return client_list
    except Exception as ex:
        print(ex)
        logger.error(f"Error: {ex}")
        raise HTTPException(500, detail=str(ex))

@app.get("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
def get_client_by_id(client_id: int, conn=Depends(get_db)):
    try:
        client: ClientResponse = helpers.ClientHelper.find_first_by_field(conn, 
                                                                         "id", 
                                                                         client_id)
        return client
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.post("/clients/", response_model=ClientResponse, status_code=201, tags=["Clients"])
def create_client(client_data: ClientRequest, conn=Depends(get_db)):
    try:
        new_client: ClientResponse = helpers.ClientHelper.create(conn, client_data)
        return new_client
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.put("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
def update_client(client_id: int, client_data: ClientRequest, conn=Depends(get_db)):
    try:
        client: ClientResponse = helpers.ClientHelper.update(conn, 
                                                        client_id, 
                                                        client_data)
        return client
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/clients/{client_id}", status_code=204, tags=["Clients"])
def delete_client(client_id: int, conn=Depends(get_db)):
    try:
        helpers.ClientHelper.delete(conn, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

# --- Client User CRUD Endpoints ---
@app.get("/clients/{client_id}/users/", response_model=List[CompanyUser], tags=["Client Users"])
def get_client_users(client_id: int, conn=Depends(get_db)):
    try:
        users_list: List[CompanyUser] = helpers.CompanyUserHelper.find_all(conn, client_id)
        return users_list
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(500, detail=str(ex))
    
@app.get("/clients/{client_id}/users/{user_id}", response_model=List[CompanyUser], tags=["Client Users"])
def get_client_user_by_id(client_id: int, user_id: int, conn=Depends(get_db)):
    try:
        user: CompanyUser = helpers.CompanyUserHelper.find_first_by_field(conn, 
                                                                         user_id, 
                                                                         client_id)
        return user
    except Exception as ex:

        raise HTTPException(500, detail=str(ex))

@app.post("/clients/{client_id}/users/", response_model=CompanyUser, status_code=201, tags=["Client Users"])
def add_user_to_client(client_id: int, new_user: CompanyUserRequest, conn=Depends(get_db)):
    try:
        new_user: CompanyUser = helpers.CompanyUserHelper.create(conn, new_user, client_id)
        return new_user
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/clients/{client_id}/users/{user_id}", response_model=CompanyUser, tags=["Client Users"])
def update_client_user(client_id: int, user_id: int, user_update: CompanyUserRequest, conn=Depends(get_db)):
    try:
        new_user: CompanyUser = helpers.CompanyUserHelper.update(conn, 
                                                                 user_id, 
                                                                 user_update, 
                                                                 client_id)
        return new_user
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/clients/{client_id}/users/{user_id}", status_code=204, tags=["Client Users"])
def delete_client_user(client_id: int, user_id: int, conn=Depends(get_db)):
    try:
        helpers.CompanyUserHelper.delete(conn, user_id, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

# --- Account Type CRUD Endpoints ---
@app.get("/account-types/", response_model=List[AccountType], tags=["Account Configuration"])
def get_account_types(conn=Depends(get_db)):
    try:
        account: AccountType = helpers.AccountTypeHelper.find_all(conn)
        return account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/account-types/", response_model=AccountType, status_code=201, tags=["Account Configuration"])
def create_account_type(acc_type: AccountType, conn=Depends(get_db)):
    try:
        new_acc: AccountType = helpers.AccountTypeHelper.create(conn, acc_type)
        return new_acc
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/account-types/{account_id}", response_model=AccountType, tags=["Account Configuration"])
def update_account_type(account_id: int, acc_update: AccountType, conn=Depends(get_db)):
    try:
        new_acc: AccountType = helpers.AccountTypeHelper.update(conn, 
                                                                 account_id, 
                                                                 acc_update)
        return new_acc
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/account-types/{account_id}", status_code=204, tags=["Account Configuration"])
def delete_account_type(account_id: int, conn=Depends(get_db)):
    try:
        helpers.AccountTypeHelper.delete(conn, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

# --- Account Currency CRUD Endpoints ---
@app.get("/account-currencies/", response_model=List[AccountCurrency], tags=["Account Configuration"])
def get_account_currencies(conn=Depends(get_db)):
    try:
        account: AccountCurrency = helpers.AccountCurrencyHelper.find_all(conn)
        return account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/account-currencies/", response_model=AccountCurrency, status_code=201, tags=["Account Configuration"])
def create_account_currencies(acc: AccountCurrency, conn=Depends(get_db)):
    try:
        new_acc: AccountCurrency = helpers.AccountCurrencyHelper.create(conn, acc)
        return new_acc
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/account-currencies/{account_id}", response_model=AccountCurrency, tags=["Account Configuration"])
def update_account_currencies(account_id: int, acc_update: AccountCurrency, conn=Depends(get_db)):
    try:
        new_acc: AccountCurrency = helpers.AccountCurrencyHelper.update(conn, 
                                                                 account_id, 
                                                                 acc_update)
        return new_acc
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/account-currencies/{account_id}", status_code=204, tags=["Account Configuration"])
def delete_account_currencies(account_id: int, conn=Depends(get_db)):
    try:
        helpers.AccountCurrencyHelper.delete(conn, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
# --- Account Balance CRUD Endpoints ---
@app.get("/account-balance/", response_model=List[AccountBalance], tags=["Account Configuration"])
def get_every_account_balance(conn=Depends(get_db)):
    try:
        balance: AccountBalance = helpers.AccountBalanceHelper.find_all(conn)
        return balance
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.get("/account-balance/{account_id}", response_model=List[AccountBalance], tags=["Account Configuration"])
def get_account_balances_from_account(account_id: int, conn=Depends(get_db)):
    try:
        balance: AccountBalance = helpers.AccountBalanceHelper.find_all_by_account(conn, account_id)
        return balance
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.get("/account-balance/{account_id}/{balance_id}", response_model=List[AccountBalance], tags=["Account Configuration"])
def get_account_balance(account_id: int, balance_id: int, conn=Depends(get_db)):
    try:
        balance: AccountBalance = helpers.AccountBalanceHelper.find_first_by_id(conn, balance_id=balance_id, account_id=account_id)
        return balance
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/account-balance/{account_id}", status_code=201, tags=["Account Configuration"])
def create_account_balance(balance: AccountBalance, account_id: int, conn=Depends(get_db)):
    try:
        helpers.AccountBalanceHelper.create(conn, balance, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/account-balance/{account_id}/{balance_id}", response_model=AccountBalance, tags=["Account Configuration"])
def update_account_balance(balance_id: int, account_id: int, balance: AccountBalance, conn=Depends(get_db)):
    try:
        new_balance: AccountBalance = helpers.AccountBalanceHelper.update(conn, 
                                                                          balance_id,
                                                                          balance,
                                                                          account_id)
        return new_balance
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/account-balance/{account_id}/{balance_id}", status_code=204, tags=["Account Configuration"])
def delete_account_balance(balance_id: int, account_id: int, conn=Depends(get_db)):
    try:
        helpers.AccountBalanceHelper.delete(conn, balance_id, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

# --- Financial Account CRUD Endpoints ---
@app.get("/clients/{client_id}/accounts/", response_model=List[Account], tags=["Financial Accounts"])
def get_all_financial_accounts_for_client(client_id: int, conn=Depends(get_db)):
    try:
        account: Account = helpers.AccountHelper.find_all(conn, client_id)
        return account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.get("/clients/{client_id}/accounts/{account_id}", response_model=Account, tags=["Financial Accounts"])
def get_financial_account(client_id: int, account_id: int, conn=Depends(get_db)):
    try:
        account: Account = helpers.AccountHelper.find_first_by_id(conn, 
                                                                         account_id, 
                                                                         client_id)
        return account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/clients/{client_id}/accounts/", response_model=Account, status_code=201, tags=["Financial Accounts"])
def create_financial_account(client_id: int, account_data: Account, conn=Depends(get_db)):
    try:
        new_account: Account = helpers.AccountHelper.create(conn, account_data, client_id)
        return new_account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/clients/{client_id}/accounts/{account_id}", response_model=Account, tags=["Financial Accounts"])
def update_financial_account(client_id: int, account_id: int, account_data: Account, conn=Depends(get_db)):
    try:
        new_account: Account = helpers.AccountHelper.update(conn, 
                                                                 account_id, 
                                                                 account_data, 
                                                                 client_id)
        return new_account
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/clients/{client_id}/accounts/{account_id}", status_code=204, tags=["Financial Accounts"])
def delete_financial_account(client_id: int, account_id: int, conn=Depends(get_db)):
    try:
        helpers.CompanyUserHelper.delete(conn, account_id, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

# --- Transaction Status CRUD Endpoints ---
@app.get("/transaction-status/", response_model=List[TransactionStatus], tags=["Transaction Status"])
def get_transaction_status(conn=Depends(get_db)):
    try:
        transaction_status: TransactionStatus = helpers.TransactionStatusHelper.find_all(conn)
        return transaction_status
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/transaction-status/", response_model=TransactionStatus, status_code=201, tags=["Transaction Status"])
def create_transaction_status(transaction_status: TransactionStatus, conn=Depends(get_db)):
    try:
        new_transaction_status: TransactionStatus = helpers.TransactionStatusHelper.create(conn, transaction_status)
        return new_transaction_status
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/transaction-status/{transaction_id}", response_model=TransactionStatus, tags=["Transaction Status"])
def update_transaction_status(transaction_id: int, transaction_status_update: TransactionStatus, conn=Depends(get_db)):
    try:
        new_transaction_status: TransactionStatus = helpers.TransactionStatusHelper.update(conn, 
                                                                 transaction_id, 
                                                                 transaction_status_update)
        return new_transaction_status
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/transaction-status/{transaction_id}", status_code=204, tags=["Transaction Status"])
def delete_transaction_status(transaction_id: int, conn=Depends(get_db)):
    try:
        helpers.TransactionStatusHelper.delete(conn, transaction_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
# --- Invoice CRUD Endpoints ---
@app.get("/invoice/", response_model=List[Invoice], tags=["Invoice"])
def get_invoice(conn=Depends(get_db)):
    try:
        invoice: Invoice = helpers.InvoiceHelper.find_all(conn)
        return invoice
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/invoice/", response_model=Invoice, status_code=201, tags=["Invoice"])
def create_invoice(invoice: Invoice, conn=Depends(get_db)):
    try:
        new_invoice: Invoice = helpers.InvoiceHelper.create(conn, invoice)
        return new_invoice
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/invoice/{invoice_id}", response_model=Invoice, tags=["Invoice"])
def update_invoice(invoice_id: int, invoice_update: Invoice, conn=Depends(get_db)):
    try:
        new_invoice: Invoice = helpers.InvoiceHelper.update(conn, 
                                                                 invoice_id, 
                                                                 invoice_update)
        return new_invoice
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/invoice/{invoice_id}", status_code=204, tags=["Invoice"])
def delete_invoice(invoice_id: int, conn=Depends(get_db)):
    try:
        helpers.InvoiceHelper.delete(conn, invoice_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
# --- Partner CRUD Endpoints ---
@app.get("/partner/", response_model=List[Partner], tags=["Partner"])
def get_partner(conn=Depends(get_db)):
    try:
        partner: Partner = helpers.PartnerHelper.find_all(conn)
        return partner
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/partner/", status_code=201, tags=["Partner"])
def create_partner(partner: Partner, conn=Depends(get_db)):
    try:
        helpers.PartnerHelper.create(conn, partner)
        
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/partner/{partner_id}", response_model=Partner, tags=["Partner"])
def update_partner(partner_id: int, partner_update: Partner, conn=Depends(get_db)):
    try:
        new_partner: Partner = helpers.PartnerHelper.update(conn, 
                                                                 partner_id, 
                                                                 partner_update)
        return new_partner
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/partner/{partner_id}", status_code=204, tags=["Partner"])
def delete_partner(partner_id: int, conn=Depends(get_db)):
    try:
        helpers.PartnerHelper.delete(conn, partner_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
# --- Category CRUD Endpoints ---
@app.get("/category/", response_model=List[CategoryResponse], tags=["Category"])
def get_category(conn=Depends(get_db)):
    try:
        category: CategoryResponse = helpers.CategoryHelper.find_all(conn)
        return category
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/category/", response_model=CategoryResponse, status_code=201, tags=["Category"])
def create_category(category: CategoryRequest, conn=Depends(get_db)):
    try:
        new_category: CategoryResponse = helpers.CategoryHelper.create(conn, category)
        return new_category
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/category/{category_id}", response_model=CategoryResponse, tags=["Category"])
def update_category(category_id: int, category_update: CategoryRequest, conn=Depends(get_db)):
    try:
        new_category: CategoryResponse = helpers.CategoryHelper.update(conn, 
                                                                 category_id, 
                                                                 category_update)
        return new_category
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/category/{category_id}", status_code=204, tags=["Category"])
def delete_category(category_id: int, conn=Depends(get_db)):
    try:
        helpers.CategoryHelper.delete(conn, category_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
# --- Cost Center CRUD Endpoints ---
@app.get("/cost-center/", response_model=List[CostCenter], tags=["Cost Center"])
def get_cost_center(conn=Depends(get_db)):
    try:
        cost_center: CostCenter = helpers.CostCenterHelper.find_all(conn)
        return cost_center
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/cost-center/", response_model=CostCenter, status_code=201, tags=["Cost Center"])
def create_cost_center(cost_center: CostCenter, conn=Depends(get_db)):
    try:
        new_cost_center: CostCenter = helpers.CostCenterHelper.create(conn, cost_center)
        return new_cost_center
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/cost-center/{cost_center_id}", response_model=CostCenter, tags=["Cost Center"])
def update_cost_center(cost_center_id: int, cost_center_update: CostCenter, conn=Depends(get_db)):
    try:
        new_cost_center: CostCenter = helpers.CostCenterHelper.update(conn, 
                                                                 cost_center_id, 
                                                                 cost_center_update)
        return new_cost_center
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/cost-center/{cost_center_id}", status_code=204, tags=["Cost Center"])
def delete_cost_center(cost_center_id: int, conn=Depends(get_db)):
    try:
        helpers.CostCenterHelper.delete(conn, cost_center_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# --- Transactions CRUD Endpoints ---
@app.get("/transactions/", response_model=List[Transaction], tags=["Transactions"])
def get_every_account_transaction(conn=Depends(get_db)):
    try:
        transaction_list: List[Transaction] = helpers.TransactionHelper.find_all(conn)
        return transaction_list
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.get("/transactions/{account_id}", response_model=List[Transaction], tags=["Transactions"])
def get_account_transactions_from_account(account_id: int, conn=Depends(get_db)):
    try:
        transaction_list: List[Transaction] = helpers.TransactionHelper.find_all_by_account(conn, account_id)
        return transaction_list
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))
    
@app.get("/transactions/{account_id}/{transaction_id}", response_model=List[Transaction], tags=["Transactions"])
def get_account_transaction(account_id: int, transaction_id: int, conn=Depends(get_db)):
    try:
        transaction: Transaction = helpers.TransactionHelper.find_first_by_id(conn, transaction_id=transaction_id, account_id=account_id)
        return transaction
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.post("/transactions/{account_id}", status_code=201, tags=["Transactions"])
def create_account_transaction(transaction: Transaction, account_id: int, conn=Depends(get_db)):
    try:
        helpers.TransactionHelper.create(conn, transaction, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.put("/transactions/{account_id}/{transaction_id}", response_model=Transaction, tags=["Transactions"])
def update_account_transaction(transaction_id: int, account_id: int, transaction: Transaction, conn=Depends(get_db)):
    try:
        new_transaction: Transaction = helpers.TransactionHelper.update(conn, 
                                                                          transaction_id,
                                                                          transaction,
                                                                          account_id)
        return new_transaction
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.delete("/transactions/{account_id}/{transaction_id}", status_code=204, tags=["Transactions"])
def delete_account_transaction(transaction_id: int, account_id: int, conn=Depends(get_db)):
    try:
        helpers.TransactionHelper.delete(conn, transaction_id, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))