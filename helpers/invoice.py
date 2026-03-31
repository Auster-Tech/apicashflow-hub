from fastapi import FastAPI, HTTPException, status, Path
from typing import Any, List, Optional, Tuple, Dict, TypeVar
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum
from models import *
from pymysql.connections import Connection
from .query import Query

class InvoiceHelper:
    table = 'Invoice'
    
    @staticmethod
    def find_all(connection: Connection):
        invoice_list: List[Invoice] = []
        query = Query(InvoiceHelper.table, connection, status = Status.ACTIVE.value)
        result = query.find()
        
        
        
        for invoice in result:
            invoice_list.append(Invoice.model_validate(invoice))

        return invoice_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any):
        conditions = dict()
        conditions[field_name] = field_value
        query = Query(InvoiceHelper.table, connection, **conditions)
        result = query.find(first=True)
        
        
        
        response: Invoice = Invoice.model_validate(result)

        return response

    @staticmethod
    def find_first_by_id(connection: Connection, invoice_id: int):
        response: Invoice = InvoiceHelper.find_first_by_field(connection, "id", invoice_id)

        return response
        
    @staticmethod
    def create(connection: Connection, invoice_data: Invoice):
        invoice = invoice_data.model_dump()
        invoice['status'] = invoice['status'].value
        query = Query(InvoiceHelper.table, connection, **invoice)
        query.create()

        response: Invoice  = InvoiceHelper.find_first_by_field(connection, "invoice_number", invoice["invoice_number"])

        return response
    
    @staticmethod
    def update(connection: Connection, id:int, invoice_data: Invoice):
        invoice = invoice_data.model_dump()
        invoice['status'] = invoice['status'].value
        invoice['id'] = id
        query = Query(InvoiceHelper.table, connection, **invoice)
        query.update()

        updated_invoice: Invoice = InvoiceHelper.find_first_by_field(connection, "id", id)
        return updated_invoice

    @staticmethod
    def delete(connection: Connection, id:int):
        query = Query(InvoiceHelper.table, connection, id=id)
        query.delete()
        return True