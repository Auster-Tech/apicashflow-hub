from typing import Any, List
from models import CompanyUserRequest, CompanyUserResponse, Status
from pymysql.connections import Connection
from .query import Query


class CompanyUserHelper:
    table = 'ClientUsers'

    @staticmethod
    def find_all(connection: Connection, client_id: int) -> List[CompanyUserResponse]:
        result = Query(CompanyUserHelper.table, connection, client_id=client_id, status=Status.ACTIVE.value).find()
        return [CompanyUserResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any, client_id: int) -> CompanyUserResponse:
        result = Query(
            CompanyUserHelper.table, connection,
            **{field_name: field_value, 'client_id': client_id, 'status': Status.ACTIVE.value}
        ).find(first=True)
        return CompanyUserResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, user_id: int, client_id: int) -> CompanyUserResponse:
        return CompanyUserHelper.find_first_by_field(connection, "id", user_id, client_id)

    @staticmethod
    def create(connection: Connection, data: CompanyUserRequest, client_id: int) -> CompanyUserResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['client_id'] = client_id
        Query(CompanyUserHelper.table, connection, **payload).create()
        return CompanyUserHelper.find_first_by_field(connection, "email", payload["email"], client_id)

    @staticmethod
    def update(connection: Connection, id: int, data: CompanyUserRequest, client_id: int) -> CompanyUserResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        payload['client_id'] = client_id
        Query(CompanyUserHelper.table, connection, **payload).update()
        return CompanyUserHelper.find_first_by_field(connection, "id", id, client_id)

    @staticmethod
    def delete(connection: Connection, id: int, client_id: int) -> bool:
        Query(CompanyUserHelper.table, connection, id=id, client_id=client_id).delete()
        return True