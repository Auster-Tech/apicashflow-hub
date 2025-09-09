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
from typing import List, Optional, Tuple, Dict, Type
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum
from routers import account_currencies, account_types, client_account, client_transactions, client_users, clients

from test.database import *

# --- Initialize FastAPI App ---
app = FastAPI(
    title="Accounting Control API",
    description="An API for accountants to manage their clients' financial data.",
    version="1.0.0",
)





# --- API Endpoints ---
@app.get("/")
def read_root(): return {"message": "Welcome to the Accounting Control API!"}

app.include_router(clients.router, prefix='/clients')
app.include_router(client_users.router, prefix='/client/{client_id}/users')
app.include_router(account_types.router, prefix='/account-types')
app.include_router(account_currencies.router, prefix='/account-currencies')
app.include_router(client_account.router, prefix='/client/{client_id}/accounts')
app.include_router(client_transactions.router, prefix='/client/{client_id}/transactions')

# --- Generic CRUD Endpoints for Configuration ---
def add_generic_crud_endpoints(tag: str, db_list: list, model: Type[BaseModel], id_counter_name: str):
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



