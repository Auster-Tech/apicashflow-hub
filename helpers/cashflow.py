from typing import Optional, List
from datetime import date, datetime, timedelta
from decimal import Decimal
from pymysql.connections import Connection
from .query import Query
from models import Status


class CashflowHelper:
    """
    Aggregates Transaction data to produce cashflow summaries.
    All amounts are taken directly from the Transaction table.
    Positive amounts  → inflow (income)
    Negative amounts  → outflow (expense)
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_date_filter(period: str, reference_date: Optional[date] = None) -> tuple[date, date]:
        """Return (start_date, end_date) for the requested period."""
        today = reference_date or date.today()

        if period == "monthly":
            start = today.replace(day=1)
            # last day of month
            if today.month == 12:
                end = today.replace(month=12, day=31)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        elif period == "quarterly":
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            start = today.replace(month=quarter_start_month, day=1)
            end_month = quarter_start_month + 2
            if end_month == 12:
                end = date(today.year, 12, 31)
            else:
                end = date(today.year, end_month + 1, 1) - timedelta(days=1)

        else:  # yearly (default)
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)

        return start, end

    @staticmethod
    def _fetch_transactions(
        connection: Connection,
        client_id: Optional[int],
        start_date: date,
        end_date: date,
    ) -> List[dict]:
        """
        Fetch active transactions for the given client (or all clients if None)
        within [start_date, end_date], joining with Account to filter by client.
        """
        with connection.cursor() as cursor:
            if client_id is not None:
                sql = """
                    SELECT t.id, t.transaction_date, t.amount,
                           t.category_id, t.account_id,
                           t.cost_center_id, t.partner_id
                    FROM `Transaction` t
                    INNER JOIN `Account` a ON a.id = t.account_id
                    WHERE t.status = %s
                      AND a.client_id = %s
                      AND DATE(t.transaction_date) BETWEEN %s AND %s
                    ORDER BY t.transaction_date ASC
                """
                cursor.execute(sql, (Status.ACTIVE.value, client_id,
                                     start_date.isoformat(), end_date.isoformat()))
            else:
                sql = """
                    SELECT t.id, t.transaction_date, t.amount,
                           t.category_id, t.account_id,
                           t.cost_center_id, t.partner_id
                    FROM `Transaction` t
                    WHERE t.status = %s
                      AND DATE(t.transaction_date) BETWEEN %s AND %s
                    ORDER BY t.transaction_date ASC
                """
                cursor.execute(sql, (Status.ACTIVE.value,
                                     start_date.isoformat(), end_date.isoformat()))
            return cursor.fetchall()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def get_summary(
        connection: Connection,
        period: str = "yearly",
        client_id: Optional[int] = None,
    ) -> dict:
        """
        Return a cashflow summary dict with:
          - totals  (total_inflow, total_outflow, net_cash_flow)
          - monthly_breakdown  (list of {month, inflow, outflow, net_flow})
          - trend   (list of {date, cumulative_balance})
          - category_breakdown  (list of {category_id, name, amount, type})
          - account_breakdown   (list of {account_id, name, balance})
        """
        start_date, end_date = CashflowHelper._build_date_filter(period)
        rows = CashflowHelper._fetch_transactions(connection, client_id, start_date, end_date)

        # ── Totals ────────────────────────────────────────────────────
        total_inflow  = Decimal("0")
        total_outflow = Decimal("0")

        # Monthly buckets  {  "YYYY-MM": {"inflow": D, "outflow": D}  }
        monthly: dict[str, dict] = {}

        # Cumulative trend  [ {date, cumulative_balance} ]
        trend_by_date: dict[str, Decimal] = {}

        # Per-category totals  { category_id: Decimal }
        category_totals: dict[int, Decimal] = {}

        # Per-account totals  { account_id: Decimal }
        account_totals: dict[int, Decimal] = {}

        for row in rows:
            amount = Decimal(str(row["amount"] or 0))
            tx_date: datetime = row["transaction_date"]
            if isinstance(tx_date, str):
                tx_date = datetime.fromisoformat(tx_date)

            month_key = tx_date.strftime("%Y-%m")
            date_key  = tx_date.strftime("%Y-%m-%d")

            # monthly buckets
            if month_key not in monthly:
                monthly[month_key] = {"inflow": Decimal("0"), "outflow": Decimal("0")}

            if amount >= 0:
                total_inflow += amount
                monthly[month_key]["inflow"] += amount
            else:
                total_outflow += abs(amount)
                monthly[month_key]["outflow"] += abs(amount)

            # daily cumulative
            trend_by_date[date_key] = trend_by_date.get(date_key, Decimal("0")) + amount

            # category
            cat_id = row.get("category_id")
            if cat_id is not None:
                category_totals[cat_id] = category_totals.get(cat_id, Decimal("0")) + amount

            # account
            acc_id = row.get("account_id")
            if acc_id is not None:
                account_totals[acc_id] = account_totals.get(acc_id, Decimal("0")) + amount

        net_cash_flow = total_inflow - total_outflow

        # ── Monthly breakdown (sorted) ────────────────────────────────
        monthly_breakdown = [
            {
                "month":    mk,
                "inflow":   float(v["inflow"]),
                "outflow":  float(v["outflow"]),
                "net_flow": float(v["inflow"] - v["outflow"]),
            }
            for mk, v in sorted(monthly.items())
        ]

        # ── Cumulative trend ──────────────────────────────────────────
        cumulative = Decimal("0")
        trend = []
        for d_key in sorted(trend_by_date.keys()):
            cumulative += trend_by_date[d_key]
            trend.append({"date": d_key, "cumulative_balance": float(cumulative)})

        # ── Category breakdown (enrich with names) ────────────────────
        category_breakdown = []
        if category_totals:
            ids_in = ", ".join(str(i) for i in category_totals.keys())
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT id, name, type FROM `Category` WHERE id IN ({ids_in})"
                )
                cat_rows = cursor.fetchall()
            cat_map = {r["id"]: r for r in cat_rows}
            for cat_id, total in category_totals.items():
                cat = cat_map.get(cat_id, {})
                category_breakdown.append({
                    "category_id": cat_id,
                    "name":        cat.get("name", f"Category {cat_id}"),
                    "type":        cat.get("type", "unknown"),
                    "amount":      float(abs(total)),
                })
            category_breakdown.sort(key=lambda x: x["amount"], reverse=True)

        # ── Account breakdown (enrich with names) ─────────────────────
        account_breakdown = []
        if account_totals:
            ids_in = ", ".join(str(i) for i in account_totals.keys())
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT id, name FROM `Account` WHERE id IN ({ids_in})"
                )
                acc_rows = cursor.fetchall()
            acc_map = {r["id"]: r for r in acc_rows}
            for acc_id, total in account_totals.items():
                acc = acc_map.get(acc_id, {})
                account_breakdown.append({
                    "account_id": acc_id,
                    "name":       acc.get("name", f"Account {acc_id}"),
                    "balance":    float(total),
                })

        return {
            "period":      period,
            "start_date":  start_date.isoformat(),
            "end_date":    end_date.isoformat(),
            "totals": {
                "total_inflow":   float(total_inflow),
                "total_outflow":  float(total_outflow),
                "net_cash_flow":  float(net_cash_flow),
            },
            "monthly_breakdown":  monthly_breakdown,
            "trend":              trend,
            "category_breakdown": category_breakdown,
            "account_breakdown":  account_breakdown,
        }
