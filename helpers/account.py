from typing import Any, List
from models import AccountRequest, AccountResponse, Status
from pymysql.connections import Connection
from .query import Query


class AccountHelper:
    table = 'Account'

    @staticmethod
    def find_all(connection: Connection, client_id: int) -> List[AccountResponse]:
        result = Query(AccountHelper.table, connection, client_id=client_id, status=Status.ACTIVE.value).find()
        return [AccountResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any, client_id: int) -> AccountResponse:
        result = Query(
            AccountHelper.table, connection,
            **{field_name: field_value, 'client_id': client_id, 'status': Status.ACTIVE.value}
        ).find(first=True)
        return AccountResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, account_id: int, client_id: int) -> AccountResponse:
        return AccountHelper.find_first_by_field(connection, "id", account_id, client_id)

    @staticmethod
    def create(connection: Connection, data: AccountRequest, client_id: int) -> AccountResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['client_id'] = client_id
        id = Query(AccountHelper.table, connection, **payload).create()
        account = AccountHelper.find_first_by_id(connection, id, client_id)
        return account

    @staticmethod
    def update(connection: Connection, id: int, data: AccountRequest, client_id: int) -> AccountResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        payload['client_id'] = client_id
        Query(AccountHelper.table, connection, **payload).update()
        return AccountHelper.find_first_by_field(connection, "id", id, client_id)

    @staticmethod
    def delete(connection: Connection, id: int, client_id: int) -> bool:
        Query(AccountHelper.table, connection, id=id, client_id=client_id).delete()
        return True
