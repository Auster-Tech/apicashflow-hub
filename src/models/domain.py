# --- Pydantic Models (Data Schemas) ---
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum

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