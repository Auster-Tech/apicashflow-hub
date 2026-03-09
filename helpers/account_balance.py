from typing import Any, List
from models import *
from pymysql.connections import Connection
from .query import Query

class AccountBalanceHelper:
    table = 'AccountBalance'
    
    @staticmethod
    def find_all(connection: Connection):
        account_list: List[AccountBalance] = []
        query = Query(AccountBalanceHelper.table, connection, status = Status.ACTIVE.value)
        result = query.find()
        
        if not result:
            raise Exception("No result found.")
        
        for account in result:
            account_list.append(AccountBalance.model_validate(account))

        return account_list 

    @staticmethod
    def find_all_by_account(connection: Connection, account_id: int):
        account_list: List[AccountBalance] = []
        query = Query(AccountBalanceHelper.table, connection, status = Status.ACTIVE.value, account_id = account_id)
        result = query.find()
        
        if not result:
            raise Exception("No result found.")
        
        for account in result:
            account_list.append(AccountBalance.model_validate(account))

        return account_list 
    
    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any, account_id: int):
        conditions = dict()
        conditions[field_name] = field_value
        conditions['account_id'] = account_id
        conditions['status'] = Status.ACTIVE.value
        query = Query(AccountBalanceHelper.table, connection, **conditions)
        result = query.find(first=True)
        
        if not result:
            raise Exception("No result found.")
        
        response: AccountBalance = AccountBalance.model_validate(result)

        return response

    @staticmethod
    def find_first_by_id(connection: Connection, balance_id: int, account_id: int):
        response: AccountBalance = AccountBalanceHelper.find_first_by_field(connection, "id", balance_id, account_id)

        return response
        
    @staticmethod
    def create(connection: Connection, balance_data: AccountBalance, account_id: int):
        account = balance_data.model_dump()
        account['status'] = account['status'].value
        account['account_id'] = account_id
        query = Query(AccountBalanceHelper.table, connection, **account)
        query.create()

        return True
    
    @staticmethod
    def update(connection: Connection, id: int, balance_data: AccountBalance, account_id: int):
        account = balance_data.model_dump()
        account['status'] = account['status'].value
        account['id'] = id
        account['account_id'] = account_id
        query = Query(AccountBalanceHelper.table, connection, **account)
        query.update()

        updated_account: AccountBalance = AccountBalanceHelper.find_first_by_field(connection, "id", id)
        return updated_account

    @staticmethod
    def delete(connection: Connection, id:int, account_id: int):
        query = Query(AccountBalanceHelper.table, connection, id=id, account_id=account_id)
        query.delete()
        return True