from typing import Any, List
from models import *
from pymysql.connections import Connection
from .query import Query

class AccountHelper:
    table = 'Account'
    
    @staticmethod
    def find_all(connection: Connection, client_id: int):
        client_list: List[Account] = []
        query = Query(AccountHelper.table, connection, client_id = client_id, status = Status.ACTIVE.value)
        result = query.find()

        

        for client in result:
            client_list.append(Account.model_validate(client))

        return client_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any, client_id: int):
        conditions = dict()
        conditions[field_name] = field_value
        conditions['client_id'] = client_id
        conditions['status'] = Status.ACTIVE.value
        query = Query(AccountHelper.table, connection, **conditions)
        result = query.find(first=True)

        

        response: Account = Account.model_validate(result)

        return response

    @staticmethod
    def find_first_by_id(connection: Connection, account_id: int, client_id: int):
        response: Account = AccountHelper.find_first_by_field(connection, "id", account_id, client_id)

        return response
        
    @staticmethod
    def create(connection: Connection, account_data: Account, client_id: int):
        account = account_data.model_dump()
        account['status'] = account['status'].value
        account['client_id'] = client_id
        query = Query(AccountHelper.table, connection, **account)
        query.create()

        return True
    
    @staticmethod
    def update(connection: Connection, id:int, account_data: Account, client_id: int):
        account = account_data.model_dump()
        account['status'] = account['status'].value
        account['id'] = id
        account['client_id'] = client_id
        query = Query(AccountHelper.table, connection, **account)
        query.update()

        updated_account: Account = AccountHelper.find_first_by_field(connection, "id", id)
        return updated_account

    @staticmethod
    def delete(connection: Connection, id:int, client_id: int):
        query = Query(AccountHelper.table, connection, id=id, client_id=client_id)
        query.delete()
        return True