from typing import Any, List
from models import PartnerRequest, PartnerResponse, Status
from pymysql.connections import Connection
from .query import Query


class PartnerHelper:
    table = 'Partner'

    @staticmethod
    def find_all(connection: Connection) -> List[PartnerResponse]:
        result = Query(PartnerHelper.table, connection, status=Status.ACTIVE.value).find()
        return [PartnerResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any) -> PartnerResponse:
        result = Query(PartnerHelper.table, connection, **{field_name: field_value}).find(first=True)
        return PartnerResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, partner_id: int) -> PartnerResponse:
        return PartnerHelper.find_first_by_field(connection, "id", partner_id)

    @staticmethod
    def create(connection: Connection, data: PartnerRequest) -> bool:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        Query(PartnerHelper.table, connection, **payload).create()
        return True

    @staticmethod
    def update(connection: Connection, id: int, data: PartnerRequest) -> PartnerResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        Query(PartnerHelper.table, connection, **payload).update()
        return PartnerHelper.find_first_by_field(connection, "id", id)

    @staticmethod
    def delete(connection: Connection, id: int) -> bool:
        Query(PartnerHelper.table, connection, id=id).delete()
        return True
