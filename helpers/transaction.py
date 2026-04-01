from typing import Any, List
from models import TransactionRequest, TransactionResponse, Status
from pymysql.connections import Connection
from .query import Query


class TransactionHelper:
    table = 'Transaction'

    @staticmethod
    def find_all(connection: Connection) -> List[TransactionResponse]:
        result = Query(TransactionHelper.table, connection, status=Status.ACTIVE.value).find()
        return [TransactionResponse.model_validate(row) for row in result]

    @staticmethod
    def find_all_by_account(connection: Connection, account_id: int) -> List[TransactionResponse]:
        result = Query(TransactionHelper.table, connection, status=Status.ACTIVE.value, account_id=account_id).find()
        return [TransactionResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any, account_id: int) -> TransactionResponse:
        result = Query(
            TransactionHelper.table, connection,
            **{field_name: field_value, 'account_id': account_id, 'status': Status.ACTIVE.value}
        ).find(first=True)
        return TransactionResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, transaction_id: int, account_id: int) -> TransactionResponse:
        return TransactionHelper.find_first_by_field(connection, "id", transaction_id, account_id)

    @staticmethod
    def create(connection: Connection, data: TransactionRequest, account_id: int) -> bool:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['account_id'] = account_id
        # Convert date to string for MySQL
        payload['transaction_date'] = str(payload['transaction_date'])
        Query(TransactionHelper.table, connection, **payload).create()
        return True

    @staticmethod
    def update(connection: Connection, id: int, data: TransactionRequest, account_id: int) -> TransactionResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        payload['account_id'] = account_id
        payload['transaction_date'] = str(payload['transaction_date'])
        Query(TransactionHelper.table, connection, **payload).update()
        return TransactionHelper.find_first_by_field(connection, "id", id, account_id)

    @staticmethod
    def delete(connection: Connection, id: int, account_id: int) -> bool:
        Query(TransactionHelper.table, connection, id=id, account_id=account_id).delete()
        return True
