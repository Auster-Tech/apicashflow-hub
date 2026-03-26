from fastapi import FastAPI, HTTPException, status, Path
from typing import Any, List, Optional, Tuple, Dict, TypeVar
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum
from models import *
from pymysql.connections import Connection
from .query import Query

class PartnerHelper:
    table = 'Partner'
    
    @staticmethod
    def find_all(connection: Connection):
        partner_list: List[Partner] = []
        query = Query(PartnerHelper.table, connection, status = Status.ACTIVE.value)
        result = query.find()
        
        
        
        for partner in result:
            partner_list.append(Partner.model_validate(partner))

        return partner_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any):
        conditions = dict()
        conditions[field_name] = field_value
        query = Query(PartnerHelper.table, connection, **conditions)
        result = query.find(first=True)
        
        
        
        response: Partner = Partner.model_validate(result)

        return response

    @staticmethod
    def find_first_by_id(connection: Connection, partner_id: int):
        response: Partner = PartnerHelper.find_first_by_field(connection, "id", partner_id)

        return response
        
    @staticmethod
    def create(connection: Connection, partner_data: Partner):
        partner = partner_data.model_dump()
        partner['status'] = partner['status'].value
        query = Query(PartnerHelper.table, connection, **partner)
        query.create()
        return True
    
    @staticmethod
    def update(connection: Connection, id:int, partner_data: Partner):
        partner = partner_data.model_dump()
        partner['status'] = partner['status'].value
        partner['id'] = id
        query = Query(PartnerHelper.table, connection, **partner)
        query.update()

        updated_partner: Partner = PartnerHelper.find_first_by_field(connection, "id", id)
        return updated_partner

    @staticmethod
    def delete(connection: Connection, id:int):
        query = Query(PartnerHelper.table, connection, id=id)
        query.delete()
        return True