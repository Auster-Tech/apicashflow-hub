from typing import Any, List, Optional
from models import TransactionStatusRequest, TransactionStatusResponse, Status
from pymysql.connections import Connection
from .query import Query


class TransactionStatusHelper:
    table = 'TransactionStatus'

    @staticmethod
    def find_all(connection: Connection, client_id: Optional[int] = None) -> List[TransactionStatusResponse]:
        filters = {'status': Status.ACTIVE.value}
        if client_id is not None:
            filters['client_id'] = client_id
        result = Query(TransactionStatusHelper.table, connection, **filters).find()
        return [TransactionStatusResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any) -> TransactionStatusResponse:
        result = Query(TransactionStatusHelper.table, connection, **{field_name: field_value}).find(first=True)
        return TransactionStatusResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, transaction_status_id: int) -> TransactionStatusResponse:
        return TransactionStatusHelper.find_first_by_field(connection, "id", transaction_status_id)

    @staticmethod
    def create(connection: Connection, data: TransactionStatusRequest) -> TransactionStatusResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        Query(TransactionStatusHelper.table, connection, **payload).create()
        return TransactionStatusHelper.find_first_by_field(connection, "name", payload["name"])

    @staticmethod
    def update(connection: Connection, id: int, data: TransactionStatusRequest) -> TransactionStatusResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        Query(TransactionStatusHelper.table, connection, **payload).update()
        return TransactionStatusHelper.find_first_by_field(connection, "id", id)

    @staticmethod
    def delete(connection: Connection, id: int) -> bool:
        Query(TransactionStatusHelper.table, connection, id=id).delete()
        return True
