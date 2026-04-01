from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
from datetime import date
from enum import Enum


# --- Enums ---

class Status(Enum):
    INACTIVE = 0
    ACTIVE = 1
    SUSPENDED = 2
    DELETED = 99

class CategoryType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"


# --- CompanyUser ---

class CompanyUserRequest(BaseModel):
    name: str
    email: EmailStr
    is_admin: bool = Field(..., alias='isAdmin')
    status: Status

    class Config:
        validate_by_name = True

class CompanyUserResponse(CompanyUserRequest):
    id: int


# --- Client ---

class ClientRequest(BaseModel):
    tax_id: str = Field(..., alias='taxId')
    company_name: str = Field(..., alias='companyName')
    industry: str
    email: EmailStr
    phone: str
    address: str
    fiscal_year_end: str = Field(..., alias='fiscalYearEnd')
    status: Status

    class Config:
        validate_by_name = True

class ClientResponse(ClientRequest):
    id: int


# --- AccountType ---

class AccountTypeRequest(BaseModel):
    name: str = Field(..., description="The unique name of the account type.")
    status: Status

class AccountTypeResponse(AccountTypeRequest):
    id: int


# --- AccountCurrency ---

class AccountCurrencyRequest(BaseModel):
    code: str = Field(..., description="The unique three-letter currency code (e.g., BRL).")
    name: str = Field(..., description="The full name of the currency.")
    status: Status

class AccountCurrencyResponse(AccountCurrencyRequest):
    id: int


# --- Account ---

class AccountRequest(BaseModel):
    name: str
    institution: str
    account_type_id: int
    account_currency_id: int
    client_id: int
    status: Status

class AccountResponse(AccountRequest):
    id: int


# --- AccountBalance ---

class AccountBalanceRequest(BaseModel):
    account_id: int
    balance: Decimal
    status: Status
    dt_created: str

class AccountBalanceResponse(AccountBalanceRequest):
    id: int


# --- Category ---

class CategoryRequest(BaseModel):
    name: str
    description: Optional[str] = None
    type: CategoryType
    status: Status
    client_id: int

class CategoryResponse(CategoryRequest):
    id: int


# --- TransactionStatus ---

class TransactionStatusRequest(BaseModel):
    name: str
    description: Optional[str] = None
    status: Status
    client_id: int

class TransactionStatusResponse(TransactionStatusRequest):
    id: int


# --- Partner ---

class PartnerRequest(BaseModel):
    name: str
    contact_info: Optional[str] = None
    status: Status
    client_id: int

class PartnerResponse(PartnerRequest):
    id: int


# --- CostCenter ---

class CostCenterRequest(BaseModel):
    name: str
    description: Optional[str] = None
    status: Status
    client_id: int

class CostCenterResponse(CostCenterRequest):
    id: int


# --- Invoice ---

class InvoiceRequest(BaseModel):
    invoice_number: str
    issue_date: date
    due_date: date
    amount: Decimal
    status: Status
    client_id: int

class InvoiceResponse(InvoiceRequest):
    id: int


# --- Transaction ---

class TransactionRequest(BaseModel):
    transaction_date: date = Field(..., alias="date")
    description: str
    amount: Decimal
    category_id: int = Field(..., alias="categoryId")
    account_id: int = Field(..., alias="financialAccountId")
    transaction_status_id: int = Field(..., alias="transactionStatusId")
    partner_id: Optional[int] = Field(None, alias="partnerId")
    cost_center_id: Optional[int] = Field(None, alias="costCenterId")
    invoice_id: Optional[int] = Field(None, alias="invoiceId")
    status: Status

    class Config:
        validate_by_name = True

class TransactionResponse(TransactionRequest):
    id: int


# ---------------------------------------------------------------------------
# Backward-compatibility aliases
# These keep the old names working so helpers and main.py can be migrated
# incrementally without breaking anything.
# ---------------------------------------------------------------------------

# CompanyUser kept as-is (already had Request/Response split)
CompanyUser = CompanyUserResponse

# Flat model aliases (old code used a single class for everything)
AccountType     = AccountTypeResponse
AccountCurrency = AccountCurrencyResponse
Account         = AccountResponse
AccountBalance  = AccountBalanceResponse
TransactionStatus = TransactionStatusResponse
Partner         = PartnerResponse
CostCenter      = CostCenterResponse
Invoice         = InvoiceResponse
Transaction     = TransactionResponse