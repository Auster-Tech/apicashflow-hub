# 6. Run the development server:
#    uvicorn main:app --reload
#
# 7. Open your browser and go to http://127.0.0.1:8000/docs to see the interactive API documentation.

from contextlib import asynccontextmanager
from datetime import date
import logging
from fastapi import Depends, FastAPI, HTTPException, Query as QueryParam
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from models import (
    ClientRequest, CompanyUserRequest,
    AccountTypeRequest, AccountCurrencyRequest,
    AccountRequest, AccountBalanceRequest,
    CategoryRequest, TransactionStatusRequest,
    PartnerRequest, CostCenterRequest,
    InvoiceRequest, TransactionRequest,
    ClientResponse, CompanyUserResponse,
    AccountTypeResponse, AccountCurrencyResponse,
    AccountResponse, AccountBalanceResponse,
    CategoryResponse, TransactionStatusResponse,
    PartnerResponse, CostCenterResponse,
    InvoiceResponse, TransactionResponse,
    EnrichedTransactionResponse,
)
import helpers
import pymysql
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
        cursorclass=pymysql.cursors.DictCursor,
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

app = FastAPI(
    title="Accounting Control API",
    description="An API for accountants to manage their clients' financial data.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# --- Root ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Accounting Control API!"}


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

@app.get("/clients/", response_model=List[ClientResponse], tags=["Clients"])
def get_all_clients(conn=Depends(get_db)):
    try:
        return helpers.ClientHelper.find_all(conn)
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(500, detail=str(ex))


@app.get("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
def get_client_by_id(client_id: int, conn=Depends(get_db)):
    try:
        return helpers.ClientHelper.find_first_by_field(conn, "id", client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/clients/", response_model=ClientResponse, status_code=201, tags=["Clients"])
def create_client(client_data: ClientRequest, conn=Depends(get_db)):
    try:
        return helpers.ClientHelper.create(conn, client_data)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
def update_client(client_id: int, client_data: ClientRequest, conn=Depends(get_db)):
    try:
        return helpers.ClientHelper.update(conn, client_id, client_data)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/clients/{client_id}", status_code=204, tags=["Clients"])
def delete_client(client_id: int, conn=Depends(get_db)):
    try:
        helpers.ClientHelper.delete(conn, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Client Users
# ---------------------------------------------------------------------------

@app.get("/clients/{client_id}/users/", response_model=List[CompanyUserResponse], tags=["Client Users"])
def get_client_users(client_id: int, conn=Depends(get_db)):
    try:
        return helpers.CompanyUserHelper.find_all(conn, client_id)
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(500, detail=str(ex))


@app.get("/clients/{client_id}/users/{user_id}", response_model=CompanyUserResponse, tags=["Client Users"])
def get_client_user_by_id(client_id: int, user_id: int, conn=Depends(get_db)):
    try:
        return helpers.CompanyUserHelper.find_first_by_id(conn, user_id, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/clients/{client_id}/users/", response_model=CompanyUserResponse, status_code=201, tags=["Client Users"])
def add_user_to_client(client_id: int, new_user: CompanyUserRequest, conn=Depends(get_db)):
    try:
        return helpers.CompanyUserHelper.create(conn, new_user, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/clients/{client_id}/users/{user_id}", response_model=CompanyUserResponse, tags=["Client Users"])
def update_client_user(client_id: int, user_id: int, user_update: CompanyUserRequest, conn=Depends(get_db)):
    try:
        return helpers.CompanyUserHelper.update(conn, user_id, user_update, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/clients/{client_id}/users/{user_id}", status_code=204, tags=["Client Users"])
def delete_client_user(client_id: int, user_id: int, conn=Depends(get_db)):
    try:
        helpers.CompanyUserHelper.delete(conn, user_id, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Client Transactions  ← NEW
# ---------------------------------------------------------------------------
@app.get(
    "/clients/{client_id}/transactions/",
    response_model=List[EnrichedTransactionResponse],
    tags=["Transactions"],
    summary="Get all transactions for a client (across all their accounts)",
)
def get_client_transactions(
    client_id: int,
    start_date: Optional[date] = QueryParam(None, description="Filter from this date (YYYY-MM-DD). Optional."),
    end_date:   Optional[date] = QueryParam(None, description="Filter up to this date (YYYY-MM-DD). Optional."),
    conn=Depends(get_db),
):
    """
    Return all transactions for a client's accounts, optionally filtered by
    date range.  When no dates are supplied the full history is returned.
 
    Examples
    --------
    All transactions:
        GET /clients/1/transactions/
 
    Current year (sent by the frontend by default):
        GET /clients/1/transactions/?start_date=2026-01-01&end_date=2026-12-31
 
    Single month:
        GET /clients/1/transactions/?start_date=2026-03-01&end_date=2026-03-31
    """
    try:
        return helpers.TransactionHelper.find_all_by_client(
            conn,
            client_id=client_id,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(status_code=500, detail=str(ex))
# ---------------------------------------------------------------------------
# Account Types
# ---------------------------------------------------------------------------

@app.get("/account-types/", response_model=List[AccountTypeResponse], tags=["Account Configuration"])
def get_account_types(conn=Depends(get_db)):
    try:
        return helpers.AccountTypeHelper.find_all(conn)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/account-types/", response_model=AccountTypeResponse, status_code=201, tags=["Account Configuration"])
def create_account_type(acc_type: AccountTypeRequest, conn=Depends(get_db)):
    try:
        return helpers.AccountTypeHelper.create(conn, acc_type)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/account-types/{account_id}", response_model=AccountTypeResponse, tags=["Account Configuration"])
def update_account_type(account_id: int, acc_update: AccountTypeRequest, conn=Depends(get_db)):
    try:
        return helpers.AccountTypeHelper.update(conn, account_id, acc_update)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/account-types/{account_id}", status_code=204, tags=["Account Configuration"])
def delete_account_type(account_id: int, conn=Depends(get_db)):
    try:
        helpers.AccountTypeHelper.delete(conn, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Account Currencies
# ---------------------------------------------------------------------------

@app.get("/account-currencies/", response_model=List[AccountCurrencyResponse], tags=["Account Configuration"])
def get_account_currencies(conn=Depends(get_db)):
    try:
        return helpers.AccountCurrencyHelper.find_all(conn)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/account-currencies/", response_model=AccountCurrencyResponse, status_code=201, tags=["Account Configuration"])
def create_account_currency(acc: AccountCurrencyRequest, conn=Depends(get_db)):
    try:
        return helpers.AccountCurrencyHelper.create(conn, acc)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/account-currencies/{account_id}", response_model=AccountCurrencyResponse, tags=["Account Configuration"])
def update_account_currency(account_id: int, acc_update: AccountCurrencyRequest, conn=Depends(get_db)):
    try:
        return helpers.AccountCurrencyHelper.update(conn, account_id, acc_update)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/account-currencies/{account_id}", status_code=204, tags=["Account Configuration"])
def delete_account_currency(account_id: int, conn=Depends(get_db)):
    try:
        helpers.AccountCurrencyHelper.delete(conn, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Account Balances
# ---------------------------------------------------------------------------

@app.get("/account-balance/", response_model=List[AccountBalanceResponse], tags=["Account Configuration"])
def get_every_account_balance(conn=Depends(get_db)):
    try:
        return helpers.AccountBalanceHelper.find_all(conn)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.get("/account-balance/{account_id}", response_model=List[AccountBalanceResponse], tags=["Account Configuration"])
def get_account_balances_from_account(account_id: int, conn=Depends(get_db)):
    try:
        return helpers.AccountBalanceHelper.find_all_by_account(conn, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.get("/account-balance/{account_id}/{balance_id}", response_model=AccountBalanceResponse, tags=["Account Configuration"])
def get_account_balance(account_id: int, balance_id: int, conn=Depends(get_db)):
    try:
        return helpers.AccountBalanceHelper.find_first_by_id(conn, balance_id=balance_id, account_id=account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/account-balance/{account_id}", status_code=201, tags=["Account Configuration"])
def create_account_balance(balance: AccountBalanceRequest, account_id: int, conn=Depends(get_db)):
    try:
        helpers.AccountBalanceHelper.create(conn, balance, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/account-balance/{account_id}/{balance_id}", response_model=AccountBalanceResponse, tags=["Account Configuration"])
def update_account_balance(balance_id: int, account_id: int, balance: AccountBalanceRequest, conn=Depends(get_db)):
    try:
        return helpers.AccountBalanceHelper.update(conn, balance_id, balance, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/account-balance/{account_id}/{balance_id}", status_code=204, tags=["Account Configuration"])
def delete_account_balance(balance_id: int, account_id: int, conn=Depends(get_db)):
    try:
        helpers.AccountBalanceHelper.delete(conn, balance_id, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Financial Accounts
# ---------------------------------------------------------------------------

@app.get("/clients/{client_id}/accounts/", response_model=List[AccountResponse], tags=["Financial Accounts"])
def get_all_financial_accounts_for_client(client_id: int, conn=Depends(get_db)):
    try:
        return helpers.AccountHelper.find_all(conn, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.get("/clients/{client_id}/accounts/{account_id}", response_model=AccountResponse, tags=["Financial Accounts"])
def get_financial_account(client_id: int, account_id: int, conn=Depends(get_db)):
    try:
        return helpers.AccountHelper.find_first_by_id(conn, account_id, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/clients/{client_id}/accounts/", response_model=AccountResponse, status_code=201, tags=["Financial Accounts"])
def create_financial_account(client_id: int, account_data: AccountRequest, conn=Depends(get_db)):
    try:
        return helpers.AccountHelper.create(conn, account_data, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/clients/{client_id}/accounts/{account_id}", response_model=AccountResponse, tags=["Financial Accounts"])
def update_financial_account(client_id: int, account_id: int, account_data: AccountRequest, conn=Depends(get_db)):
    try:
        return helpers.AccountHelper.update(conn, account_id, account_data, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/clients/{client_id}/accounts/{account_id}", status_code=204, tags=["Financial Accounts"])
def delete_financial_account(client_id: int, account_id: int, conn=Depends(get_db)):
    try:
        helpers.AccountHelper.delete(conn, account_id, client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Transaction Status
# ---------------------------------------------------------------------------

@app.get("/transaction-status/", response_model=List[TransactionStatusResponse], tags=["Transaction Status"])
def get_transaction_status(
    client_id: Optional[int] = QueryParam(None),
    conn=Depends(get_db),
):
    try:
        return helpers.TransactionStatusHelper.find_all(conn, client_id=client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/transaction-status/", response_model=TransactionStatusResponse, status_code=201, tags=["Transaction Status"])
def create_transaction_status(transaction_status: TransactionStatusRequest, conn=Depends(get_db)):
    try:
        return helpers.TransactionStatusHelper.create(conn, transaction_status)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/transaction-status/{transaction_id}", response_model=TransactionStatusResponse, tags=["Transaction Status"])
def update_transaction_status(transaction_id: int, transaction_status_update: TransactionStatusRequest, conn=Depends(get_db)):
    try:
        return helpers.TransactionStatusHelper.update(conn, transaction_id, transaction_status_update)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/transaction-status/{transaction_id}", status_code=204, tags=["Transaction Status"])
def delete_transaction_status(transaction_id: int, conn=Depends(get_db)):
    try:
        helpers.TransactionStatusHelper.delete(conn, transaction_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

@app.get("/invoice/", response_model=List[InvoiceResponse], tags=["Invoice"])
def get_invoice(
    client_id: Optional[int] = QueryParam(None),
    conn=Depends(get_db),
):
    try:
        return helpers.InvoiceHelper.find_all(conn, client_id=client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/invoice/", response_model=InvoiceResponse, status_code=201, tags=["Invoice"])
def create_invoice(invoice: InvoiceRequest, conn=Depends(get_db)):
    try:
        return helpers.InvoiceHelper.create(conn, invoice)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/invoice/{invoice_id}", response_model=InvoiceResponse, tags=["Invoice"])
def update_invoice(invoice_id: int, invoice_update: InvoiceRequest, conn=Depends(get_db)):
    try:
        return helpers.InvoiceHelper.update(conn, invoice_id, invoice_update)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/invoice/{invoice_id}", status_code=204, tags=["Invoice"])
def delete_invoice(invoice_id: int, conn=Depends(get_db)):
    try:
        helpers.InvoiceHelper.delete(conn, invoice_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Partners
# ---------------------------------------------------------------------------

@app.get("/partner/", response_model=List[PartnerResponse], tags=["Partner"])
def get_partner(
    client_id: Optional[int] = QueryParam(None),
    conn=Depends(get_db),
):
    try:
        return helpers.PartnerHelper.find_all(conn, client_id=client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/partner/", status_code=201, tags=["Partner"])
def create_partner(partner: PartnerRequest, conn=Depends(get_db)):
    try:
        helpers.PartnerHelper.create(conn, partner)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/partner/{partner_id}", response_model=PartnerResponse, tags=["Partner"])
def update_partner(partner_id: int, partner_update: PartnerRequest, conn=Depends(get_db)):
    try:
        return helpers.PartnerHelper.update(conn, partner_id, partner_update)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/partner/{partner_id}", status_code=204, tags=["Partner"])
def delete_partner(partner_id: int, conn=Depends(get_db)):
    try:
        helpers.PartnerHelper.delete(conn, partner_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@app.get("/category/", response_model=List[CategoryResponse], tags=["Category"])
def get_category(
    client_id: Optional[int] = QueryParam(None),
    conn=Depends(get_db),
):
    try:
        return helpers.CategoryHelper.find_all(conn, client_id=client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/category/", response_model=CategoryResponse, status_code=201, tags=["Category"])
def create_category(category: CategoryRequest, conn=Depends(get_db)):
    try:
        return helpers.CategoryHelper.create(conn, category)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/category/{category_id}", response_model=CategoryResponse, tags=["Category"])
def update_category(category_id: int, category_update: CategoryRequest, conn=Depends(get_db)):
    try:
        return helpers.CategoryHelper.update(conn, category_id, category_update)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/category/{category_id}", status_code=204, tags=["Category"])
def delete_category(category_id: int, conn=Depends(get_db)):
    try:
        helpers.CategoryHelper.delete(conn, category_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Cost Centers
# ---------------------------------------------------------------------------

@app.get("/cost-center/", response_model=List[CostCenterResponse], tags=["Cost Center"])
def get_cost_center(
    client_id: Optional[int] = QueryParam(None),
    conn=Depends(get_db),
):
    try:
        return helpers.CostCenterHelper.find_all(conn, client_id=client_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/cost-center/", response_model=CostCenterResponse, status_code=201, tags=["Cost Center"])
def create_cost_center(cost_center: CostCenterRequest, conn=Depends(get_db)):
    try:
        return helpers.CostCenterHelper.create(conn, cost_center)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/cost-center/{cost_center_id}", response_model=CostCenterResponse, tags=["Cost Center"])
def update_cost_center(cost_center_id: int, cost_center_update: CostCenterRequest, conn=Depends(get_db)):
    try:
        return helpers.CostCenterHelper.update(conn, cost_center_id, cost_center_update)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/cost-center/{cost_center_id}", status_code=204, tags=["Cost Center"])
def delete_cost_center(cost_center_id: int, conn=Depends(get_db)):
    try:
        helpers.CostCenterHelper.delete(conn, cost_center_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

@app.get("/transactions/", response_model=List[EnrichedTransactionResponse], tags=["Transactions"])
def get_every_account_transaction(conn=Depends(get_db)):
    try:
        return helpers.TransactionHelper.find_all(conn)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.get("/transactions/{account_id}", response_model=List[EnrichedTransactionResponse], tags=["Transactions"])
def get_account_transactions_from_account(account_id: int, conn=Depends(get_db)):
    try:
        return helpers.TransactionHelper.find_all_by_account(conn, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.get("/transactions/{account_id}/{transaction_id}", response_model=EnrichedTransactionResponse, tags=["Transactions"])
def get_account_transaction(account_id: int, transaction_id: int, conn=Depends(get_db)):
    try:
        return helpers.TransactionHelper.find_first_by_id(
            conn, transaction_id=transaction_id, account_id=account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.post("/transactions/{account_id}", status_code=201, tags=["Transactions"])
def create_account_transaction(transaction: TransactionRequest, account_id: int, conn=Depends(get_db)):
    try:
        helpers.TransactionHelper.create(conn, transaction, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.put("/transactions/{account_id}/{transaction_id}", response_model=EnrichedTransactionResponse, tags=["Transactions"])
def update_account_transaction(transaction_id: int, account_id: int, transaction: TransactionRequest, conn=Depends(get_db)):
    try:
        return helpers.TransactionHelper.update(conn, transaction_id, transaction, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))


@app.delete("/transactions/{account_id}/{transaction_id}", status_code=204, tags=["Transactions"])
def delete_account_transaction(transaction_id: int, account_id: int, conn=Depends(get_db)):
    try:
        helpers.TransactionHelper.delete(conn, transaction_id, account_id)
    except Exception as ex:
        raise HTTPException(500, detail=str(ex))

@app.get("/cashflow/", tags=["Cashflow"])
def get_cashflow(
    period: str = QueryParam("yearly"),          # monthly | quarterly | yearly
    client_id: Optional[int] = QueryParam(None),
    conn=Depends(get_db),
):
    """
    Returns an aggregated cashflow summary for the given period.
 
    Query parameters
    ----------------
    period    : "monthly" | "quarterly" | "yearly"  (default: "yearly")
    client_id : filter by a specific client (optional for accountants)
 
    Response structure
    ------------------
    {
      "period": "yearly",
      "start_date": "2026-01-01",
      "end_date":   "2026-12-31",
      "totals": {
        "total_inflow":  12345.67,
        "total_outflow":  9876.54,
        "net_cash_flow":  2469.13
      },
      "monthly_breakdown": [
        { "month": "2026-01", "inflow": 1000, "outflow": 800, "net_flow": 200 },
        ...
      ],
      "trend": [
        { "date": "2026-01-05", "cumulative_balance": 200.0 },
        ...
      ],
      "category_breakdown": [
        { "category_id": 3, "name": "Salário", "type": "income", "amount": 5000 },
        ...
      ],
      "account_breakdown": [
        { "account_id": 1, "name": "Conta Corrente", "balance": 1500.0 },
        ...
      ]
    }
    """
    if period not in ("monthly", "quarterly", "yearly"):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="Invalid period. Must be one of: monthly, quarterly, yearly",
        )
    try:
        return helpers.CashflowHelper.get_summary(
            conn,
            period=period,
            client_id=client_id,
        )
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(500, detail=str(ex))