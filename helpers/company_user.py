from fastapi import FastAPI, HTTPException, status, Path
from typing import Any, List, Optional, Tuple, Dict, TypeVar
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum
from models import *
from pymysql.connections import Connection
from .query import Query

class CompanyUserHelper:
    table = 'ClientUsers'
    
    @staticmethod
    def find_all(connection: Connection, client_id: int):
        client_list: List[CompanyUser] = []
        query = Query(CompanyUserHelper.table, connection, client_id = client_id, status = Status.ACTIVE.value)
        result = query.find()
        
        if not result:
            raise Exception("No result found.")
        
        for client in result:
            client_list.append(CompanyUser.model_validate(client))

        return client_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any, client_id: int):
        conditions = dict()
        conditions[field_name] = field_value
        conditions['client_id'] = client_id
        conditions['status'] = Status.ACTIVE.value
        query = Query(CompanyUserHelper.table, connection, **conditions)
        result = query.find(first=True)
        
        if not result:
            raise Exception("No result found.")
        
        response: CompanyUser = CompanyUser.model_validate(result)

        return response

    @staticmethod
    def find_first_by_id(connection: Connection, user_id: int, client_id: int):
        response: CompanyUser = CompanyUserHelper.find_first_by_field(connection, "id", user_id, client_id)

        return response
        
    @staticmethod
    def create(connection: Connection, client_data: CompanyUser, client_id: int):
        client = client_data.model_dump()
        client['status'] = client['status'].value
        client['client_id'] = client_id
        query = Query(CompanyUserHelper.table, connection, **client)
        query.create()

        response: CompanyUser = CompanyUserHelper.find_first_by_field(connection, "email", client["email"])
        
        return response
    
    @staticmethod
    def update(connection: Connection, id:int, client_data: CompanyUser, client_id: int):
        client = client_data.model_dump()
        client['status'] = client['status'].value
        client['id'] = id
        client['client_id'] = client_id
        query = Query(CompanyUserHelper.table, connection, **client)
        query.update()

        updated_client: CompanyUser = CompanyUserHelper.find_first_by_field(connection, "id", id)
        return updated_client

    @staticmethod
    def delete(connection: Connection, id:int, client_id: int):
        query = Query(CompanyUserHelper.table, connection, id=id, client_id=client_id)
        query.delete()
        return True