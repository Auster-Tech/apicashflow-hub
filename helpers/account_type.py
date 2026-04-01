from typing import Any, List
from models import AccountTypeRequest, AccountTypeResponse, Status
from pymysql.connections import Connection
from .query import Query


class AccountTypeHelper:
    table = 'AccountType'

    @staticmethod
    def find_all(connection: Connection) -> List[AccountTypeResponse]:
        result = Query(AccountTypeHelper.table, connection, status=Status.ACTIVE.value).find()
        return [AccountTypeResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any) -> AccountTypeResponse:
        result = Query(AccountTypeHelper.table, connection, **{field_name: field_value}).find(first=True)
        return AccountTypeResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, account_type_id: int) -> AccountTypeResponse:
        return AccountTypeHelper.find_first_by_field(connection, "id", account_type_id)

    @staticmethod
    def create(connection: Connection, data: AccountTypeRequest) -> AccountTypeResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        Query(AccountTypeHelper.table, connection, **payload).create()
        return AccountTypeHelper.find_first_by_field(connection, "name", payload["name"])

    @staticmethod
    def update(connection: Connection, id: int, data: AccountTypeRequest) -> AccountTypeResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        Query(AccountTypeHelper.table, connection, **payload).update()
        return AccountTypeHelper.find_first_by_field(connection, "id", id)

    @staticmethod
    def delete(connection: Connection, id: int) -> bool:
        Query(AccountTypeHelper.table, connection, id=id).delete()
        return True
