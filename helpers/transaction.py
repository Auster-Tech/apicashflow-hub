from typing import Any, List
from models import *
from pymysql.connections import Connection
from .query import Query

class TransactionHelper:
    table = 'Transaction'
    
    @staticmethod
    def find_all(connection: Connection):
        transaction_list: List[Transaction] = []
        query = Query(TransactionHelper.table, connection, status = Status.ACTIVE.value)
        result = query.find()
        
        if not result:
            raise Exception("No result found.")
        
        for account in result:
            transaction_list.append(Transaction.model_validate(account))

        return transaction_list 

    @staticmethod
    def find_all_by_account(connection: Connection, account_id: int):
        transaction_list: List[Transaction] = []
        query = Query(TransactionHelper.table, connection, status = Status.ACTIVE.value, account_id = account_id)
        result = query.find()
        
        if not result:
            raise Exception("No result found.")
        
        for account in result:
            transaction_list.append(Transaction.model_validate(account))

        return transaction_list 
    
    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any, account_id: int):
        conditions = dict()
        conditions[field_name] = field_value
        conditions['account_id'] = account_id
        conditions['status'] = Status.ACTIVE.value
        query = Query(TransactionHelper.table, connection, **conditions)
        result = query.find(first=True)
        
        if not result:
            raise Exception("No result found.")
        
        response: Transaction = Transaction.model_validate(result)

        return response

    @staticmethod
    def find_first_by_id(connection: Connection, transaction__id: int, account_id: int):
        response: Transaction = TransactionHelper.find_first_by_field(connection, "id", transaction__id, account_id)

        return response
        
    @staticmethod
    def create(connection: Connection, transaction_data: Transaction, account_id: int):
        transaction = transaction_data.model_dump()
        transaction['status'] = transaction['status'].value
        transaction['account_id'] = account_id
        query = Query(TransactionHelper.table, connection, **transaction)
        query.create()

        return True
    
    @staticmethod
    def update(connection: Connection, id: int, transaction_data: Transaction, account_id: int):
        transaction = transaction_data.model_dump()
        transaction['status'] = transaction['status'].value
        transaction['id'] = id
        transaction['account_id'] = account_id
        query = Query(TransactionHelper.table, connection, **transaction)
        query.update()

        updated_account: Transaction = TransactionHelper.find_first_by_field(connection, "id", id)
        return updated_account

    @staticmethod
    def delete(connection: Connection, id:int, account_id: int):
        query = Query(TransactionHelper.table, connection, id=id, account_id=account_id)
        query.delete()
        return True