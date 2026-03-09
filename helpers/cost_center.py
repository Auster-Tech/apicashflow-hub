from fastapi import FastAPI, HTTPException, status, Path
from typing import Any, List, Optional, Tuple, Dict, TypeVar
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum
from models import *
from pymysql.connections import Connection
from .query import Query

class CostCenterHelper:
    table = 'CostCenter'
    
    @staticmethod
    def find_all(connection: Connection):
        cost_center_list: List[CostCenter] = []
        query = Query(CostCenterHelper.table, connection, status = Status.ACTIVE.value)
        result = query.find()
        
        if not result:
            raise Exception("No result found.")
        
        for cost_center in result:
            cost_center_list.append(CostCenter.model_validate(cost_center))

        return cost_center_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any):
        conditions = dict()
        conditions[field_name] = field_value
        query = Query(CostCenterHelper.table, connection, **conditions)
        result = query.find(first=True)
        
        if not result:
            raise Exception("No result found.")
        
        response: CostCenter = CostCenter.model_validate(result)

        return response

    @staticmethod
    def find_first_by_id(connection: Connection, cost_center_id: int):
        response: CostCenter = CostCenterHelper.find_first_by_field(connection, "id", cost_center_id)

        return response
        
    @staticmethod
    def create(connection: Connection, cost_center_data: CostCenter):
        cost_center = cost_center_data.model_dump()
        cost_center['status'] = cost_center['status'].value
        query = Query(CostCenterHelper.table, connection, **cost_center)
        query.create()

        response: CostCenter  = CostCenterHelper.find_first_by_field(connection, "name", cost_center["name"])

        return response
    
    @staticmethod
    def update(connection: Connection, id:int, cost_center_data: CostCenter):
        cost_center = cost_center_data.model_dump()
        cost_center['status'] = cost_center['status'].value
        cost_center['id'] = id
        query = Query(CostCenterHelper.table, connection, **cost_center)
        query.update()

        updated_cost_center: CostCenter = CostCenterHelper.find_first_by_field(connection, "id", id)
        return updated_cost_center

    @staticmethod
    def delete(connection: Connection, id:int):
        query = Query(CostCenterHelper.table, connection, id=id)
        query.delete()
        return True