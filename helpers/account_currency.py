from typing import Any, List
from models import AccountCurrencyRequest, AccountCurrencyResponse, Status
from pymysql.connections import Connection
from .query import Query


class AccountCurrencyHelper:
    table = 'AccountCurrency'

    @staticmethod
    def find_all(connection: Connection) -> List[AccountCurrencyResponse]:
        result = Query(AccountCurrencyHelper.table, connection, status=Status.ACTIVE.value).find()
        return [AccountCurrencyResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any) -> AccountCurrencyResponse:
        result = Query(AccountCurrencyHelper.table, connection, **{field_name: field_value}).find(first=True)
        return AccountCurrencyResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, account_currency_id: int) -> AccountCurrencyResponse:
        return AccountCurrencyHelper.find_first_by_field(connection, "id", account_currency_id)

    @staticmethod
    def create(connection: Connection, data: AccountCurrencyRequest) -> AccountCurrencyResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        Query(AccountCurrencyHelper.table, connection, **payload).create()
        return AccountCurrencyHelper.find_first_by_field(connection, "code", payload["code"])

    @staticmethod
    def update(connection: Connection, id: int, data: AccountCurrencyRequest) -> AccountCurrencyResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        Query(AccountCurrencyHelper.table, connection, **payload).update()
        return AccountCurrencyHelper.find_first_by_field(connection, "id", id)

    @staticmethod
    def delete(connection: Connection, id: int) -> bool:
        Query(AccountCurrencyHelper.table, connection, id=id).delete()
        return True
