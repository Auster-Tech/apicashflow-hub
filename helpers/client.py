from typing import Any, List
from datetime import datetime
from models import ClientRequest, ClientResponse, Status
from pymysql.connections import Connection
from .query import Query


class ClientHelper:
    table = 'Client'

    @staticmethod
    def find_all(connection: Connection) -> List[ClientResponse]:
        result = Query(ClientHelper.table, connection, status=Status.ACTIVE.value).find()
        return [ClientResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any) -> ClientResponse:
        result = Query(
            ClientHelper.table, connection,
            **{field_name: field_value, 'status': Status.ACTIVE.value}
        ).find(first=True)
        return ClientResponse.model_validate(result)

    @staticmethod
    def create(connection: Connection, data: ClientRequest) -> ClientResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        Query(ClientHelper.table, connection, **payload).create()
        return ClientHelper.find_first_by_field(connection, "tax_id", payload["tax_id"])

    @staticmethod
    def update(connection: Connection, id: int, data: ClientRequest) -> ClientResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        Query(ClientHelper.table, connection, **payload).update()
        return ClientHelper.find_first_by_field(connection, "id", id)

    @staticmethod
    def delete(connection: Connection, id: int) -> bool:
        client: ClientResponse = ClientHelper.find_first_by_field(connection, "id", id)
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        data = dict(id=client.id, tax_id=f"{client.tax_id}-DELETED-{now}")
        Query(ClientHelper.table, connection, **data).delete()
        return True