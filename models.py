from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel, EmailStr, Field, field_validator, validator
from decimal import Decimal
from datetime import date
from enum import Enum


# --- Pydantic Models (Data Schemas) ---

class Status(Enum):
    INACTIVE = 0
    ACTIVE = 1
    SUSPENDED = 2
    DELETED = 99

class CompanyUser(BaseModel):
    id: Optional[int]
    name: str; email: EmailStr; is_admin: bool
    status: Status
    class Config: validate_by_name = True

class ClientCreate(BaseModel):
    tax_id: str = Field(..., alias='taxId')
    company_name: str = Field(..., alias='companyName')
    industry: str; email: EmailStr; phone: str; address: str
    fiscal_year_end: str = Field(..., alias='fiscalYearEnd')
    status: Status
    class Config: validate_by_name = True

class ClientResponse(ClientCreate):
    id: int

class AccountType(BaseModel):
    id: Optional[int]
    name: str = Field(..., description="The unique name of the account type.")
    status: Status

class AccountCurrency(BaseModel):
    id: Optional[int]
    code: str = Field(..., description="The unique three-letter currency code (e.g., BRL).")
    name: str = Field(..., description="The full name of the currency.")
    status: Status

class Account(BaseModel):
    id: Optional[int]
    name: str; institution: str
    account_type_id: int
    account_currency_id: int
    client_id: int
    status: Status

class AccountBalance(BaseModel):
    id: Optional[int]
    account_id: int
    balance: Decimal
    status: Status
    dt_created: str

class CategoryType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"

class CategoryRequest(BaseModel):
    name: str; description: Optional[str] = None
    type: CategoryType; status: Status

class CategoryResponse(CategoryRequest):
    id: Optional[int]

class TransactionStatus(BaseModel):
    id: Optional[int]; name: str; description: Optional[str] = None
    status: Status

class Partner(BaseModel):
    id: Optional[int]; name: str; contact_info: Optional[str] = None
    status: Status

class CostCenter(BaseModel):
    id: Optional[int]; name: str; description: Optional[str] = None
    status: Status

class Invoice(BaseModel):
    id: Optional[int]; invoice_number: str; issue_date: date; due_date: date; amount: Decimal
    status: Status

class Transaction(BaseModel):
    transaction_date: date = Field(..., alias="date")
    description: str; amount: Decimal
    category_id: int = Field(..., alias="categoryId")
    account_id: int = Field(..., alias="financialAccountId")
    transaction_status_id: int = Field(..., alias="transactionStatusId")
    partner_id: Optional[int] = Field(None, alias="partnerId")
    cost_center_id: Optional[int] = Field(None, alias="costCenterId")
    invoice_id: Optional[int] = Field(None, alias="invoiceId")
    status: Status
    class Config: validate_by_name = True

class TransactionResponse(Transaction):
    id: int