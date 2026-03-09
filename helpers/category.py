from fastapi import FastAPI, HTTPException, status, Path
from typing import Any, List, Optional, Tuple, Dict, TypeVar
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal
from datetime import date
from enum import Enum
from models import *
from pymysql.connections import Connection
from .query import Query

class CategoryHelper:
    table = 'Category'
    
    @staticmethod
    def find_all(connection: Connection):
        category_list: List[Category] = []
        query = Query(CategoryHelper.table, connection, status = Status.ACTIVE.value)
        result = query.find()
        
        if not result:
            raise Exception("No result found.")
        
        for category in result:
            category_list.append(Category.model_validate(category))

        return category_list 

    @staticmethod
    def find_first_by_field(connection: Connection, field_name:str, field_value:Any):
        conditions = dict()
        conditions[field_name] = field_value
        query = Query(CategoryHelper.table, connection, **conditions)
        result = query.find(first=True)
        
        if not result:
            raise Exception("No result found.")
        
        response: Category = Category.model_validate(result)

        return response

    @staticmethod
    def find_first_by_id(connection: Connection, category_id: int):
        response: Category = CategoryHelper.find_first_by_field(connection, "id", category_id)

        return response
        
    @staticmethod
    def create(connection: Connection, category_data: Category):
        category = category_data.model_dump()
        category['status'] = category['status'].value
        category['type'] = category['type'].value
        query = Query(CategoryHelper.table, connection, **category)
        query.create()

        response: Category  = CategoryHelper.find_first_by_field(connection, "name", category["name"])

        return response
    
    @staticmethod
    def update(connection: Connection, id:int, category_data: Category):
        category = category_data.model_dump()
        category['status'] = category['status'].value
        category['type'] = category['type'].value
        category['id'] = id
        query = Query(CategoryHelper.table, connection, **category)
        query.update()

        updated_category: Category = CategoryHelper.find_first_by_field(connection, "id", id)
        return updated_category

    @staticmethod
    def delete(connection: Connection, id:int):
        query = Query(CategoryHelper.table, connection, id=id)
        query.delete()
        return True