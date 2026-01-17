from fastapi import FastAPI, HTTPException, status, Path
from typing import Any, List, Optional, Tuple, Dict, TypeVar
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
    for i, user in enumerate(ClientHelper.users):
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
        if ClientHelper.client_id == client_id: return client
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

class Query:
    def __init__(self, table: str, connection: Connection):
        self.table = table
        self.connection = connection
    
    def find_all(self):
        with self.connection.cursor() as cursor:
            sql = F"SELECT * FROM `{ClientHelper.table}`"
            cursor.execute(sql)
            result = cursor.fetchall()
        return result
    
    def find_first_by_field(self, field_name:str, field_value:Any):
        with self.connection.cursor() as cursor:
            sql = F"SELECT * FROM `{self.table}` WHERE `{field_name}`=%s"
            cursor.execute(sql, (field_value,))
            result = cursor.fetchone()
        return result
    
    def create(self, client_data: dict):
        columns = client_data.keys()
        col_list_str = "`,`".join(columns)
        values_list = [f"%({column})s" for column in columns]
        values_list_str = ", ".join(values_list)

        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `{self.table}` (`{col_list_str}`) VALUES ({values_list_str})"
            cursor.execute(sql, client_data)

        self.connection.commit()

    def update(self, id: int, client_data: dict):
        set_values = []
        
        for column in client_data.keys():
            set_values.append(f"{column} = %({column})s")
        
        set_clause = ", ".join(set_values)
        
        with self.connection.cursor() as cursor:
            sql = f"UPDATE `{self.table}` SET {set_clause} WHERE `id` = {id}"
            cursor.execute(sql, client_data)

        self.connection.commit()

    def delete(self, id: int):
        with self.connection.cursor() as cursor:
            sql = f"UPDATE `{self.table}` SET `status` = {Status.DELETED.value} WHERE `id` = {id}"
            cursor.execute(sql)

        self.connection.commit()    

class ClientHelper:
    table = 'Client'
    
    @staticmethod
    def find_all(connection: Connection):
        client_list: List[ClientResponse] = []
        query = Query(ClientHelper.table, connection)
        result = query.find_all()
        
        if not result:
            raise Exception("No result found.")
        
        for client in result:
            client_list.append(ClientResponse.model_validate(client))

        return client_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any):
        query = Query(ClientHelper.table, connection)
        result = query.find_first_by_field(field_name, field_value)
        
        if not result:
            raise Exception("No result found.")
        
        response: ClientResponse = ClientResponse.model_validate(result)

        return response
    
    @staticmethod
    def create(connection: Connection, client_data: ClientCreate):
        client = client_data.model_dump()
        client['status'] = client['status'].value
        query = Query(ClientHelper.table, connection)
        query.create(client)
        response: ClientResponse  = ClientHelper.find_first_by_field(connection, "tax_id", client["tax_id"])

        return response
    
    @staticmethod
    def update(connection: Connection, id:int, client_data: ClientCreate):
        client = client_data.model_dump()
        client['status'] = client['status'].value
        query = Query(ClientHelper.table, connection)
        query.update(id, client)

        updated_client: ClientResponse = ClientHelper.find_first_by_field(connection, "id", id)
        return updated_client

    @staticmethod
    def delete(connection: Connection, id:int):
        query = Query(ClientHelper.table, connection)
        query.delete(id)
        return True
    
class CompanyUserHelper:
    table = 'ClientUsers'
    
    @staticmethod
    def find_all(connection: Connection):
        client_list: List[CompanyUser] = []
        query = Query(CompanyUserHelper.table, connection)
        result = query.find_all()
        
        if not result:
            raise Exception("No result found.")
        
        for client in result:
            client_list.append(CompanyUser.model_validate(client))

        return client_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any):
        query = Query(CompanyUserHelper.table, connection)
        result = query.find_first_by_field(field_name, field_value)
        
        if not result:
            raise Exception("No result found.")
        
        response: CompanyUser = CompanyUser.model_validate(result)

        return response
    
    @staticmethod
    def create(connection: Connection, client_data: CompanyUser):
        client = client_data.model_dump()
        client['status'] = client['status'].value
        query = Query(CompanyUserHelper.table, connection)
        query.create(client)
        response: CompanyUser  = CompanyUserHelper.find_first_by_field(connection, "email", client["email"])

        return response
    
    @staticmethod
    def update(connection: Connection, id:int, client_data: CompanyUser):
        client = client_data.model_dump()
        client['status'] = client['status'].value
        query = Query(CompanyUserHelper.table, connection)
        query.update(id, client)

        updated_client: CompanyUser = CompanyUserHelper.find_first_by_field(connection, "id", id)
        return updated_client

    @staticmethod
    def delete(connection: Connection, id:int):
        query = Query(CompanyUserHelper.table, connection)
        query.delete(id)
        return True