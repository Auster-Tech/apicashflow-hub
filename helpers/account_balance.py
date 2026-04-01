from typing import Any, List
from models import AccountBalanceRequest, AccountBalanceResponse, Status
from pymysql.connections import Connection
from .query import Query


class AccountBalanceHelper:
    table = 'AccountBalance'

    @staticmethod
    def find_all(connection: Connection) -> List[AccountBalanceResponse]:
        result = Query(AccountBalanceHelper.table, connection, status=Status.ACTIVE.value).find()
        return [AccountBalanceResponse.model_validate(row) for row in result]

    @staticmethod
    def find_all_by_account(connection: Connection, account_id: int) -> List[AccountBalanceResponse]:
        result = Query(AccountBalanceHelper.table, connection, status=Status.ACTIVE.value, account_id=account_id).find()
        return [AccountBalanceResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any, account_id: int) -> AccountBalanceResponse:
        result = Query(
            AccountBalanceHelper.table, connection,
            **{field_name: field_value, 'account_id': account_id, 'status': Status.ACTIVE.value}
        ).find(first=True)
        return AccountBalanceResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, balance_id: int, account_id: int) -> AccountBalanceResponse:
        return AccountBalanceHelper.find_first_by_field(connection, "id", balance_id, account_id)

    @staticmethod
    def create(connection: Connection, data: AccountBalanceRequest, account_id: int) -> bool:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['account_id'] = account_id
        Query(AccountBalanceHelper.table, connection, **payload).create()
        return True

    @staticmethod
    def update(connection: Connection, id: int, data: AccountBalanceRequest, account_id: int) -> AccountBalanceResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        payload['account_id'] = account_id
        Query(AccountBalanceHelper.table, connection, **payload).update()
        return AccountBalanceHelper.find_first_by_field(connection, "id", id, account_id)

    @staticmethod
    def delete(connection: Connection, id: int, account_id: int) -> bool:
        Query(AccountBalanceHelper.table, connection, id=id, account_id=account_id).delete()
        return True
