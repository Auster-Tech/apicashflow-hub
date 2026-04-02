from typing import Any, List, Optional
from models import CostCenterRequest, CostCenterResponse, Status
from pymysql.connections import Connection
from .query import Query


class CostCenterHelper:
    table = 'CostCenter'

    @staticmethod
    def find_all(connection: Connection, client_id: Optional[int] = None) -> List[CostCenterResponse]:
        filters = {'status': Status.ACTIVE.value}
        if client_id is not None:
            filters['client_id'] = client_id
        result = Query(CostCenterHelper.table, connection, **filters).find()
        return [CostCenterResponse.model_validate(row) for row in result]

    @staticmethod
    def find_first_by_field(connection: Connection, field_name: str, field_value: Any) -> CostCenterResponse:
        result = Query(CostCenterHelper.table, connection, **{field_name: field_value}).find(first=True)
        return CostCenterResponse.model_validate(result)

    @staticmethod
    def find_first_by_id(connection: Connection, cost_center_id: int) -> CostCenterResponse:
        return CostCenterHelper.find_first_by_field(connection, "id", cost_center_id)

    @staticmethod
    def create(connection: Connection, data: CostCenterRequest) -> CostCenterResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        Query(CostCenterHelper.table, connection, **payload).create()
        return CostCenterHelper.find_first_by_field(connection, "name", payload["name"])

    @staticmethod
    def update(connection: Connection, id: int, data: CostCenterRequest) -> CostCenterResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        Query(CostCenterHelper.table, connection, **payload).update()
        return CostCenterHelper.find_first_by_field(connection, "id", id)

    @staticmethod
    def delete(connection: Connection, id: int) -> bool:
        Query(CostCenterHelper.table, connection, id=id).delete()
        return True
