from typing import Any, List, Optional
from datetime import date
from models import (
    TransactionRequest, TransactionResponse,
    EnrichedTransactionResponse,
    EnrichedAccountInfo, EnrichedCategoryInfo, EnrichedStatusInfo,
    EnrichedCostCenterInfo, EnrichedPartnerInfo, EnrichedInvoiceInfo,
    Status,
)
from pymysql.connections import Connection
from .query import Query


class TransactionHelper:
    table = 'Transaction'

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fetch_one(connection: Connection, table: str, row_id: Optional[int]) -> Optional[dict]:
        if row_id is None:
            return None
        try:
            result = Query(table, connection, id=row_id).find(first=True)
            return result
        except Exception:
            return None

    @staticmethod
    def _enrich(connection: Connection, row: dict) -> EnrichedTransactionResponse:
        account_row      = TransactionHelper._fetch_one(connection, 'Account', row.get('account_id'))
        category_row     = TransactionHelper._fetch_one(connection, 'Category', row.get('category_id'))
        status_row       = TransactionHelper._fetch_one(connection, 'TransactionStatus', row.get('transaction_status_id'))
        cost_center_row  = TransactionHelper._fetch_one(connection, 'CostCenter', row.get('cost_center_id'))
        partner_row      = TransactionHelper._fetch_one(connection, 'Partner', row.get('partner_id'))
        invoice_row      = TransactionHelper._fetch_one(connection, 'Invoice', row.get('invoice_id'))

        account_info     = EnrichedAccountInfo(**account_row)     if account_row     else None
        category_info    = EnrichedCategoryInfo(**category_row)   if category_row    else None
        status_info      = EnrichedStatusInfo(**status_row)       if status_row      else None
        cost_center_info = EnrichedCostCenterInfo(**cost_center_row) if cost_center_row else None
        partner_info     = EnrichedPartnerInfo(**partner_row)     if partner_row     else None

        invoice_info = None
        if invoice_row:
            inv = dict(invoice_row)
            if inv.get('issue_date') is not None:
                inv['issue_date'] = str(inv['issue_date'])
            if inv.get('due_date') is not None:
                inv['due_date'] = str(inv['due_date'])
            invoice_info = EnrichedInvoiceInfo(**inv)

        transaction_date = row.get('transaction_date')
        if transaction_date is not None:
            transaction_date = str(transaction_date)

        return EnrichedTransactionResponse(
            id=row['id'],
            transaction_date=transaction_date,
            description=row.get('description'),
            amount=row.get('amount'),
            status=row.get('status'),
            category_id=row.get('category_id'),
            account_id=row.get('account_id'),
            transaction_status_id=row.get('transaction_status_id'),
            partner_id=row.get('partner_id'),
            cost_center_id=row.get('cost_center_id'),
            invoice_id=row.get('invoice_id'),
            account=account_info,
            category=category_info,
            transaction_status=status_info,
            cost_center=cost_center_info,
            partner=partner_info,
            invoice=invoice_info,
        )

    # ------------------------------------------------------------------
    # Public GET — existing (by account_id)
    # ------------------------------------------------------------------

    @staticmethod
    def find_all(connection: Connection) -> List[EnrichedTransactionResponse]:
        rows = Query(TransactionHelper.table, connection, status=Status.ACTIVE.value).find()
        return [TransactionHelper._enrich(connection, row) for row in rows]

    @staticmethod
    def find_all_by_account(
        connection: Connection, account_id: int
    ) -> List[EnrichedTransactionResponse]:
        rows = Query(
            TransactionHelper.table, connection,
            status=Status.ACTIVE.value,
            account_id=account_id,
        ).find()
        return [TransactionHelper._enrich(connection, row) for row in rows]

    @staticmethod
    def find_first_by_field(
        connection: Connection,
        field_name: str,
        field_value: Any,
        account_id: int,
    ) -> EnrichedTransactionResponse:
        row = Query(
            TransactionHelper.table, connection,
            **{field_name: field_value,
               'account_id': account_id,
               'status': Status.ACTIVE.value}
        ).find(first=True)
        return TransactionHelper._enrich(connection, row)

    @staticmethod
    def find_first_by_id(
        connection: Connection, transaction_id: int, account_id: int
    ) -> EnrichedTransactionResponse:
        return TransactionHelper.find_first_by_field(
            connection, "id", transaction_id, account_id)

    # ------------------------------------------------------------------
    # NEW — find by client_id with optional date range
    # ------------------------------------------------------------------

    @staticmethod
    def find_all_by_client(
        connection: Connection,
        client_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[EnrichedTransactionResponse]:
        """
        Return all active transactions whose account belongs to client_id.
        start_date and end_date are optional; when omitted the full history
        is returned.
        """
        params: list = [Status.ACTIVE.value, client_id]

        date_clause = ""
        if start_date is not None and end_date is not None:
            date_clause = "AND DATE(t.transaction_date) BETWEEN %s AND %s"
            params += [start_date.isoformat(), end_date.isoformat()]
        elif start_date is not None:
            date_clause = "AND DATE(t.transaction_date) >= %s"
            params.append(start_date.isoformat())
        elif end_date is not None:
            date_clause = "AND DATE(t.transaction_date) <= %s"
            params.append(end_date.isoformat())

        sql = f"""
            SELECT t.*
            FROM `Transaction` t
            INNER JOIN `Account` a ON a.id = t.account_id
            WHERE t.status = %s
              AND a.client_id = %s
              {date_clause}
            ORDER BY t.transaction_date DESC
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        return [TransactionHelper._enrich(connection, row) for row in rows]

    # ------------------------------------------------------------------
    # Write methods — unchanged
    # ------------------------------------------------------------------

    @staticmethod
    def create(
        connection: Connection, data: TransactionRequest, account_id: int
    ) -> bool:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['account_id'] = account_id
        payload['transaction_date'] = str(payload['transaction_date'])
        Query(TransactionHelper.table, connection, **payload).create()
        return True

    @staticmethod
    def update(
        connection: Connection,
        id: int,
        data: TransactionRequest,
        account_id: int,
    ) -> EnrichedTransactionResponse:
        payload = data.model_dump()
        payload['status'] = payload['status'].value
        payload['id'] = id
        payload['account_id'] = account_id
        payload['transaction_date'] = str(payload['transaction_date'])
        Query(TransactionHelper.table, connection, **payload).update()
        return TransactionHelper.find_first_by_field(
            connection, "id", id, account_id)

    @staticmethod
    def delete(
        connection: Connection, id: int, account_id: int
    ) -> bool:
        Query(TransactionHelper.table, connection,
              id=id, account_id=account_id).delete()
        return True
