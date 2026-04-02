from typing import Any, List, Optional
from models import CategoryRequest, CategoryResponse, Status
from pymysql.connections import Connection
from .query import Query


class CategoryHelper:
    table = 'Category'

    @staticmethod
    def find_all(connection: Connection, client_id: Optional[int] = None) -> List[CategoryResponse]:
        filters = {'status': Status.ACTIVE.value}
        if client_id is not None:
            filters['client_id'] = client_id
        result = Query(CategoryHelper.table, connection, **filters).find()
        return [CategoryResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any) -> CategoryResponse:
        result = Query(CategoryHelper.table, connection, **{field_name: field_value}).find(first=True)
        return CategoryResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, category_id: int) -> CategoryResponse:
        return CategoryHelper.find_first_by_field(connection, "id", category_id)

    @staticmethod
    def create(connection: Connection, data: CategoryRequest) -> CategoryResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['type'] = payload['type'].value
        Query(CategoryHelper.table, connection, **payload).create()
        return CategoryHelper.find_first_by_field(connection, "name", payload["name"])

    @staticmethod
    def update(connection: Connection, id: int, data: CategoryRequest) -> CategoryResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['type'] = payload['type'].value
        payload['id'] = id
        Query(CategoryHelper.table, connection, **payload).update()
        return CategoryHelper.find_first_by_field(connection, "id", id)

    @staticmethod
    def delete(connection: Connection, id: int) -> bool:
        Query(CategoryHelper.table, connection, id=id).delete()
        return True
