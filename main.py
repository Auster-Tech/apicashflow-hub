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

from fastapi import FastAPI, HTTPException, status, Path
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum

# --- Initialize FastAPI App ---
app = FastAPI(
    title="Accounting Control API",
    description="An API for accountants to manage their clients' financial data.",
    version="1.0.0",
)


# --- Pydantic Models (Data Schemas) ---

class CompanyUser(BaseModel):
    name: str; email: EmailStr; is_admin: bool = Field(..., alias='isAdmin')
    class Config: validate_by_name = True

class CompanyInfo(BaseModel):
    company_name: str = Field(..., alias='companyName')
    industry: str; email: EmailStr; phone: str; address: str
    fiscal_year_end: str = Field(..., alias='fiscalYearEnd')
    class Config: validate_by_name = True

class ClientCreate(BaseModel):
    company_info: CompanyInfo = Field(..., alias='companyInfo')
    users: List[CompanyUser]
    @validator('users')
    def validate_users(cls, v):
        if not v: raise ValueError('A client must have at least one user.')
        if not any(u.is_admin for u in v): raise ValueError('A client must have at least one admin user.')
        return v
    class Config: validate_by_name = True

class ClientResponse(BaseModel):
    client_id: int
    company_info: CompanyInfo
    users: List[CompanyUser]

class AccountType(BaseModel):
    name: str = Field(..., description="The unique name of the account type.")

class AccountCurrency(BaseModel):
    code: str = Field(..., description="The unique three-letter currency code (e.g., BRL).")
    name: str = Field(..., description="The full name of the currency.")

class FinancialAccountBase(BaseModel):
    name: str; institution: str
    account_type: str = Field(..., alias="accountType")
    account_currency: str = Field(..., alias="accountCurrency")
    class Config: validate_by_name = True

class FinancialAccountCreate(FinancialAccountBase):
    balance: Decimal

class FinancialAccountResponse(FinancialAccountBase):
    account_id: int; balance: Decimal

class CategoryType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"

class Category(BaseModel):
    id: int; name: str; description: Optional[str] = None
    type: CategoryType

class Status(BaseModel):
    id: int; name: str; description: Optional[str] = None

class Partner(BaseModel):
    id: int; name: str; contact_info: Optional[str] = None

class CostCenter(BaseModel):
    id: int; name: str; description: Optional[str] = None

class Invoice(BaseModel):
    id: int; invoice_number: str; issue_date: date; due_date: date; amount: Decimal

class TransactionBase(BaseModel):
    transaction_date: date = Field(..., alias="date")
    description: str; amount: Decimal
    category_id: int = Field(..., alias="categoryId")
    financial_account_id: int = Field(..., alias="financialAccountId")
    status_id: int = Field(..., alias="statusId")
    partner_id: Optional[int] = Field(None, alias="partnerId")
    cost_center_id: Optional[int] = Field(None, alias="costCenterId")
    invoice_id: Optional[int] = Field(None, alias="invoiceId")
    class Config: validate_by_name = True

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int

# --- In-Memory Database ---
db_clients: List[ClientResponse] = []
client_id_counter = 1

db_account_types: List[AccountType] = [AccountType(name=n) for n in ["Checking", "Savings", "Credit Card", "Investment"]]
db_account_currencies: List[AccountCurrency] = [
    AccountCurrency(code="BRL", name="Brazilian Real"), AccountCurrency(code="USD", name="US Dollar"), AccountCurrency(code="EUR", name="Euro")
]
db_financial_accounts: Dict[int, List[FinancialAccountResponse]] = {}
account_id_counter = 1

db_categories: List[Category] = [
    Category(id=1, name="Office Supplies", type=CategoryType.EXPENSE, description="Pens, paper, etc."),
    Category(id=2, name="Sales Revenue", type=CategoryType.INCOME, description="Primary income from sales.")
]
category_id_counter = 3

db_statuses: List[Status] = [
    Status(id=1, name="Pending", description="Transaction is awaiting confirmation."),
    Status(id=2, name="Completed", description="Transaction is finalized."),
    Status(id=3, name="Cancelled", description="Transaction was voided.")
]
status_id_counter = 4

db_partners: List[Partner] = []
partner_id_counter = 1
db_cost_centers: List[CostCenter] = []
cost_center_id_counter = 1
db_invoices: List[Invoice] = []
invoice_id_counter = 1

db_transactions: Dict[int, List[TransactionResponse]] = {}
transaction_id_counter = 1

# --- Generic Helper Functions ---
def find_item_by_id(item_id: int, db_list: list, item_name: str):
    for item in db_list:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"{item_name} with ID {item_id} not found")

# --- Specific Helper Functions ---
def find_user_by_email(client: ClientResponse, email: EmailStr):
    for i, user in enumerate(client.users):
        if user.email == email: return i, user
    return None

def find_account_type_or_404(name: str):
    for acc_type in db_account_types:
        if acc_type.name.lower() == name.lower(): return acc_type
    raise HTTPException(status_code=404, detail=f"Account type '{name}' not found.")

def find_currency_or_404(code: str):
    for currency in db_account_currencies:
        if currency.code.lower() == code.lower(): return currency
    raise HTTPException(status_code=404, detail=f"Currency code '{code}' not found.")

def find_client_or_404(client_id: int):
    for client in db_clients:
        if client.client_id == client_id: return client
    raise HTTPException(status_code=404, detail=f"Client with ID {client_id} not found")

def find_financial_account_or_404(client_id: int, account_id: int):
    if client_id not in db_financial_accounts:
        raise HTTPException(status_code=404, detail=f"No accounts found for client {client_id}")
    for account in db_financial_accounts[client_id]:
        if account.account_id == account_id: return account
    raise HTTPException(status_code=404, detail=f"Account with ID {account_id} not found for client {client_id}")

def find_transaction_or_404(client_id: int, transaction_id: int):
    if client_id not in db_transactions:
        raise HTTPException(status_code=404, detail=f"No transactions found for client {client_id}")
    for tx in db_transactions[client_id]:
        if tx.id == transaction_id: return tx
    raise HTTPException(status_code=404, detail=f"Transaction with ID {transaction_id} not found for client {client_id}")

def update_account_balance(account: FinancialAccountResponse, category: Category, amount: Decimal, operation: str):
    """Updates account balance. 'add' for new, 'subtract' for deletion/old value."""
    multiplier = -1 if category.type == CategoryType.EXPENSE else 1
    if operation == 'subtract':
        account.balance -= (amount * multiplier)
    else: # add
        account.balance += (amount * multiplier)


# --- API Endpoints ---
@app.get("/")
def read_root(): return {"message": "Welcome to the Accounting Control API!"}

# --- Client CRUD Endpoints ---
@app.post("/clients/", response_model=ClientResponse, status_code=201, tags=["Clients"])
def create_client(client_data: ClientCreate):
    global client_id_counter
    new_client = ClientResponse(client_id=client_id_counter, **client_data.dict())
    db_clients.append(new_client)
    db_financial_accounts[client_id_counter] = []
    db_transactions[client_id_counter] = []
    client_id_counter += 1
    return new_client

@app.get("/clients/", response_model=List[ClientResponse], tags=["Clients"])
def get_all_clients(): return db_clients

@app.get("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
def get_client_by_id(client_id: int): return find_client_or_404(client_id)

@app.put("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
def update_client(client_id: int, client_data: ClientCreate):
    client = find_client_or_404(client_id)
    client_index = db_clients.index(client)
    updated_client = ClientResponse(client_id=client_id, **client_data.dict())
    db_clients[client_index] = updated_client
    return updated_client

@app.delete("/clients/{client_id}", status_code=204, tags=["Clients"])
def delete_client(client_id: int):
    client = find_client_or_404(client_id)
    db_clients.remove(client)
    if client_id in db_financial_accounts:
        del db_financial_accounts[client_id]
    return None

# --- Client User CRUD Endpoints ---
@app.get("/clients/{client_id}/users/", response_model=List[CompanyUser], tags=["Client Users"])
def get_client_users(client_id: int): return find_client_or_404(client_id).users

@app.post("/clients/{client_id}/users/", response_model=CompanyUser, status_code=201, tags=["Client Users"])
def add_user_to_client(client_id: int, new_user: CompanyUser):
    client = find_client_or_404(client_id)
    if find_user_by_email(client, new_user.email):
        raise HTTPException(409, f"User with email '{new_user.email}' already exists.")
    client.users.append(new_user)
    return new_user

@app.put("/clients/{client_id}/users/{user_email}", response_model=CompanyUser, tags=["Client Users"])
def update_client_user(client_id: int, user_email: EmailStr, user_update: CompanyUser):
    client = find_client_or_404(client_id)
    user_info = find_user_by_email(client, user_email)
    if not user_info: raise HTTPException(404, f"User with email '{user_email}' not found.")
    user_index, old_user = user_info
    if old_user.is_admin and len([u for u in client.users if u.is_admin]) == 1 and not user_update.is_admin:
        raise HTTPException(400, "Cannot remove the last administrator.")
    client.users[user_index] = user_update
    return user_update

@app.delete("/clients/{client_id}/users/{user_email}", status_code=204, tags=["Client Users"])
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

# --- Account Type CRUD Endpoints ---
@app.get("/account-types/", response_model=List[AccountType], tags=["Account Configuration"])
def get_account_types(): return db_account_types

@app.post("/account-types/", response_model=AccountType, status_code=201, tags=["Account Configuration"])
def create_account_type(acc_type: AccountType):
    if any(t.name.lower() == acc_type.name.lower() for t in db_account_types):
        raise HTTPException(409, f"Account type '{acc_type.name}' already exists.")
    db_account_types.append(acc_type)
    return acc_type

# --- Account Currency CRUD Endpoints ---
@app.get("/account-currencies/", response_model=List[AccountCurrency], tags=["Account Configuration"])
def get_account_currencies(): return db_account_currencies

@app.post("/account-currencies/", response_model=AccountCurrency, status_code=201, tags=["Account Configuration"])
def create_account_currency(currency: AccountCurrency):
    if any(c.code.lower() == currency.code.lower() for c in db_account_currencies):
        raise HTTPException(409, f"Currency '{currency.code}' already exists.")
    db_account_currencies.append(currency)
    return currency

# --- Financial Account CRUD Endpoints ---
@app.post("/clients/{client_id}/accounts/", response_model=FinancialAccountResponse, status_code=201, tags=["Financial Accounts"])
def create_financial_account(client_id: int, account_data: FinancialAccountCreate):
    global account_id_counter
    find_client_or_404(client_id) # Ensure client exists
    find_account_type_or_404(account_data.account_type) # Validate type
    find_currency_or_404(account_data.account_currency) # Validate currency
    
    new_account = FinancialAccountResponse(account_id=account_id_counter, **account_data.dict())
    db_financial_accounts[client_id].append(new_account)
    account_id_counter += 1
    return new_account

@app.get("/clients/{client_id}/accounts/", response_model=List[FinancialAccountResponse], tags=["Financial Accounts"])
def get_all_financial_accounts_for_client(client_id: int):
    find_client_or_404(client_id)
    return db_financial_accounts.get(client_id, [])

@app.get("/clients/{client_id}/accounts/{account_id}", response_model=FinancialAccountResponse, tags=["Financial Accounts"])
def get_financial_account(client_id: int, account_id: int):
    return find_financial_account_or_404(client_id, account_id)

@app.put("/clients/{client_id}/accounts/{account_id}", response_model=FinancialAccountResponse, tags=["Financial Accounts"])
def update_financial_account(client_id: int, account_id: int, account_data: FinancialAccountCreate):
    find_client_or_404(client_id)
    find_account_type_or_404(account_data.account_type)
    find_currency_or_404(account_data.account_currency)
    
    account_to_update = find_financial_account_or_404(client_id, account_id)
    account_index = db_financial_accounts[client_id].index(account_to_update)
    
    updated_account = FinancialAccountResponse(account_id=account_id, **account_data.dict())
    db_financial_accounts[client_id][account_index] = updated_account
    return updated_account

@app.delete("/clients/{client_id}/accounts/{account_id}", status_code=204, tags=["Financial Accounts"])
def delete_financial_account(client_id: int, account_id: int):
    account_to_delete = find_financial_account_or_404(client_id, account_id)
    db_financial_accounts[client_id].remove(account_to_delete)
    return None

# --- Generic CRUD Endpoints for Configuration ---
def add_generic_crud_endpoints(tag: str, db_list: list, model: BaseModel, id_counter_name: str):
    plural = tag.lower()
    
    @app.get(f"/{plural}/", response_model=List[model], tags=[tag])
    def get_all(): return db_list

    @app.post(f"/{plural}/", response_model=model, status_code=201, tags=[tag])
    def create(item_data: model):
        global_vars = globals()
        new_id = global_vars[id_counter_name]
        # Simple check for name collision, can be expanded
        if hasattr(item_data, 'name') and any(i.name.lower() == item_data.name.lower() for i in db_list):
            raise HTTPException(409, f"{tag} with name '{item_data.name}' already exists.")
        new_item = model(id=new_id, **item_data.dict(exclude={'id'}))
        db_list.append(new_item)
        global_vars[id_counter_name] += 1
        return new_item

add_generic_crud_endpoints("Categories", db_categories, Category, "category_id_counter")
add_generic_crud_endpoints("Statuses", db_statuses, Status, "status_id_counter")
add_generic_crud_endpoints("Partners", db_partners, Partner, "partner_id_counter")
add_generic_crud_endpoints("CostCenters", db_cost_centers, CostCenter, "cost_center_id_counter")
add_generic_crud_endpoints("Invoices", db_invoices, Invoice, "invoice_id_counter")


# --- Transaction CRUD Endpoints ---
@app.post("/clients/{client_id}/transactions/", response_model=TransactionResponse, status_code=201, tags=["Transactions"])
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

@app.get("/clients/{client_id}/transactions/", response_model=List[TransactionResponse], tags=["Transactions"])
def get_all_transactions(client_id: int):
    find_client_or_404(client_id)
    return db_transactions.get(client_id, [])

@app.get("/clients/{client_id}/transactions/{transaction_id}", response_model=TransactionResponse, tags=["Transactions"])
def get_transaction(client_id: int, transaction_id: int):
    return find_transaction_or_404(client_id, transaction_id)

@app.put("/clients/{client_id}/transactions/{transaction_id}", response_model=TransactionResponse, tags=["Transactions"])
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

@app.delete("/clients/{client_id}/transactions/{transaction_id}", status_code=204, tags=["Transactions"])
def delete_transaction(client_id: int, transaction_id: int):
    find_client_or_404(client_id)
    tx_to_delete = find_transaction_or_404(client_id, transaction_id)
    
    # Revert the transaction's effect on the account balance
    account = find_financial_account_or_404(client_id, tx_to_delete.financial_account_id)
    category = find_item_by_id(tx_to_delete.category_id, db_categories, "Category")
    update_account_balance(account, category, tx_to_delete.amount, 'subtract')
    
    db_transactions[client_id].remove(tx_to_delete)
    return None
