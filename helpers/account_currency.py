from fastapi import FastAPI, HTTPException, status, Path
from typing import Any, List, Optional, Tuple, Dict, TypeVar
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum
from models import *
from pymysql.connections import Connection
from .query import Query

class AccountCurrencyHelper:
    table = 'AccountCurrency'
    
    @staticmethod
    def find_all(connection: Connection):
        account_list: List[AccountCurrency] = []
        query = Query(AccountCurrencyHelper.table, connection, status = Status.ACTIVE.value)
        result = query.find()
        
        if not result:
            raise Exception("No result found.")
        
        for account in result:
            account_list.append(AccountCurrency.model_validate(account))

        return account_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any):
        conditions = dict()
        conditions[field_name] = field_value
        query = Query(AccountCurrencyHelper.table, connection, **conditions)
        result = query.find(first=True)
        
        if not result:
            raise Exception("No result found.")
        
        response: AccountCurrency = AccountCurrency.model_validate(result)

        return response

    @staticmethod
    def find_first_by_id(connection: Connection, account_id: int):
        response: AccountCurrency = AccountCurrencyHelper.find_first_by_field(connection, "id", account_id)

        return response
        
    @staticmethod
    def create(connection: Connection, account_data: AccountCurrency):
        account = account_data.model_dump()
        account['status'] = account['status'].value
        query = Query(AccountCurrencyHelper.table, connection, **account)
        query.create()

        response: AccountCurrency  = AccountCurrencyHelper.find_first_by_field(connection, "code", account["code"])

        return response
    
    @staticmethod
    def update(connection: Connection, id:int, account_data: AccountCurrency):
        account = account_data.model_dump()
        account['status'] = account['status'].value
        account['id'] = id
        query = Query(AccountCurrencyHelper.table, connection, **account)
        query.update()

        updated_account: AccountCurrency = AccountCurrencyHelper.find_first_by_field(connection, "id", id)
        return updated_account

    @staticmethod
    def delete(connection: Connection, id:int):
        query = Query(AccountCurrencyHelper.table, connection, id=id)
        query.delete()
        return True