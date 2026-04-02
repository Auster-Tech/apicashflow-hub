from typing import Any, List, Optional
from models import InvoiceRequest, InvoiceResponse, Status
from pymysql.connections import Connection
from .query import Query


class InvoiceHelper:
    table = 'Invoice'

    @staticmethod
    def find_all(connection: Connection, client_id: Optional[int] = None) -> List[InvoiceResponse]:
        filters = {'status': Status.ACTIVE.value}
        if client_id is not None:
            filters['client_id'] = client_id
        result = Query(InvoiceHelper.table, connection, **filters).find()
        return [InvoiceResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any) -> InvoiceResponse:
        result = Query(InvoiceHelper.table, connection, **{field_name: field_value}).find(first=True)
        return InvoiceResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, invoice_id: int) -> InvoiceResponse:
        return InvoiceHelper.find_first_by_field(connection, "id", invoice_id)

    @staticmethod
    def create(connection: Connection, data: InvoiceRequest) -> InvoiceResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['issue_date'] = str(payload['issue_date'])
        payload['due_date'] = str(payload['due_date'])
        Query(InvoiceHelper.table, connection, **payload).create()
        return InvoiceHelper.find_first_by_field(connection, "invoice_number", payload["invoice_number"])

    @staticmethod
    def update(connection: Connection, id: int, data: InvoiceRequest) -> InvoiceResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['issue_date'] = str(payload['issue_date'])
        payload['due_date'] = str(payload['due_date'])
        payload['id'] = id
        Query(InvoiceHelper.table, connection, **payload).update()
        return InvoiceHelper.find_first_by_field(connection, "id", id)

    @staticmethod
    def delete(connection: Connection, id: int) -> bool:
        Query(InvoiceHelper.table, connection, id=id).delete()
        return True
