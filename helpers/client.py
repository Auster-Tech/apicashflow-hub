from fastapi import FastAPI, HTTPException, status, Path
from typing import Any, List, Optional, Tuple, Dict, TypeVar
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date, datetime
from enum import Enum
from models import *
from pymysql.connections import Connection
from .query import Query

class ClientHelper:
    table = 'Client'
    
    @staticmethod
    def find_all(connection: Connection):
        client_list: List[ClientResponse] = []
        query = Query(ClientHelper.table, connection, status = Status.ACTIVE.value)
        result = query.find()

        for client in result:
            client_list.append(ClientResponse.model_validate(client))

        return client_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any):
        conditions = dict()
        conditions[field_name] = field_value
        conditions['status'] = Status.ACTIVE.value
        query = Query(ClientHelper.table, connection, **conditions)
        result = query.find(first=True)

        response: ClientResponse = ClientResponse.model_validate(result)

        return response
    
    @staticmethod
    def create(connection: Connection, client_data: ClientRequest):
        client = client_data.model_dump()
        client['status'] = client['status'].value
        query = Query(ClientHelper.table, connection, **client)
        query.create()
        response: ClientResponse = ClientHelper.find_first_by_field(connection, "tax_id", client["tax_id"])

        return response
    
    @staticmethod
    def update(connection: Connection, id:int, client_data: ClientRequest):
        client = client_data.model_dump()
        client['status'] = client['status'].value
        client['id'] = id
        query = Query(ClientHelper.table, connection, **client)
        query.update()

        updated_client: ClientResponse = ClientHelper.find_first_by_field(connection, "id", id)
        return updated_client

    @staticmethod
    def delete(connection: Connection, id:int):
        client: ClientResponse = ClientHelper.find_first_by_field(connection, "id", id)
        now = datetime.now().strftime("Y-m-d-H-MS")
        data = dict(
            id=client.id,
            tax_id=f"{client.tax_id}-DELETED-{now}"
            )

        query = Query(ClientHelper.table, connection, **data)
        query.delete()
        return True
    