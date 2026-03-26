from fastapi import FastAPI, HTTPException, status, Path
from typing import Any, List, Optional, Tuple, Dict, TypeVar
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum
from models import *
from pymysql.connections import Connection
from .query import Query

class TransactionStatusHelper:
    table = 'TransactionStatus'
    
    @staticmethod
    def find_all(connection: Connection):
        transaction_status_list: List[TransactionStatus] = []
        query = Query(TransactionStatusHelper.table, connection, status = Status.ACTIVE.value)
        result = query.find()
        
        
        
        for transaction_status in result:
            transaction_status_list.append(TransactionStatus.model_validate(transaction_status))

        return transaction_status_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any):
        conditions = dict()
        conditions[field_name] = field_value
        query = Query(TransactionStatusHelper.table, connection, **conditions)
        result = query.find(first=True)
        
        
        
        response: TransactionStatus = TransactionStatus.model_validate(result)

        return response

    @staticmethod
    def find_first_by_id(connection: Connection, transaction_status_id: int):
        response: TransactionStatus = TransactionStatusHelper.find_first_by_field(connection, "id", transaction_status_id)

        return response
        
    @staticmethod
    def create(connection: Connection, transaction_status_data: TransactionStatus):
        transaction_status = transaction_status_data.model_dump()
        transaction_status['status'] = transaction_status['status'].value
        query = Query(TransactionStatusHelper.table, connection, **transaction_status)
        query.create()

        response: TransactionStatus  = TransactionStatusHelper.find_first_by_field(connection, "name", transaction_status["name"])

        return response
    
    @staticmethod
    def update(connection: Connection, id:int, transaction_status_data: TransactionStatus):
        transaction_status = transaction_status_data.model_dump()
        transaction_status['status'] = transaction_status['status'].value
        transaction_status['id'] = id
        query = Query(TransactionStatusHelper.table, connection, **transaction_status)
        query.update()

        updated_transaction_status: TransactionStatus = TransactionStatusHelper.find_first_by_field(connection, "id", id)
        return updated_transaction_status

    @staticmethod
    def delete(connection: Connection, id:int):
        query = Query(TransactionStatusHelper.table, connection, id=id)
        query.delete()
        return True