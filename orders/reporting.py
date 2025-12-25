import csv
import io
from django.db.models import Count, Sum, Q

from .models import Order
from users.models import Employee


GROUPING_VALUES = {"", "none", "client", "manager"}


def _order_period_q(period_from, period_to):
    q = Q()
    if period_from:
        q &= Q(date__gte=period_from)
    if period_to:
        q &= Q(date__lte=period_to)
    return q


def _orders_queryset(period_from, period_to):
    q = _order_period_q(period_from, period_to)
    qs = (
        Order.objects.select_related("client", "manager")
        .filter(q)
        .order_by("-date", "number")
    )
    return qs


def build_orders_report(period_from, period_to, grouping: str):
    grouping = (grouping or "").strip().lower()
    if grouping in ("", "none"):
        columns = [
            "number", "date", "client", "department", "manager",
            "status", "priority", "order_type", "planned_date", "amount_total",
        ]
        rows = []
        for o in _orders_queryset(period_from, period_to):
            rows.append({
                "number": o.number,
                "date": o.date.isoformat() if o.date else "",
                "client": str(o.client),
                "department": o.department,
                "manager": str(o.manager),
                "status": o.status,
                "priority": o.priority,
                "order_type": o.order_type,
                "planned_date": o.planned_date.isoformat() if o.planned_date else "",
                "amount_total": str(o.amount_total),
            })
        return columns, rows

    if grouping == "client":
        qs = (
            Order.objects
            .filter(_order_period_q(period_from, period_to))
            .values("client__name")
            .annotate(
                orders_count=Count("id"),
                amount_total_sum=Sum("amount_total"),
            )
            .order_by("client__name")
        )
        columns = ["client", "orders_count", "amount_total_sum"]
        rows = []
        for r in qs:
            rows.append({
                "client": r["client__name"],
                "orders_count": r["orders_count"],
                "amount_total_sum": str(r["amount_total_sum"] or 0),
            })
        return columns, rows

    if grouping == "manager":
        qs = (
            Order.objects
            .filter(_order_period_q(period_from, period_to))
            .values("manager__full_name")
            .annotate(
                orders_count=Count("id"),
                amount_total_sum=Sum("amount_total"),
            )
            .order_by("manager__full_name")
        )
        columns = ["manager", "orders_count", "amount_total_sum"]
        rows = []
        for r in qs:
            rows.append({
                "manager": r["manager__full_name"],
                "orders_count": r["orders_count"],
                "amount_total_sum": str(r["amount_total_sum"] or 0),
            })
        return columns, rows

    raise ValueError("Неверная группировка для отчёта по заказам")


def build_employees_report(period_from, period_to, grouping: str):
    # По сотрудникам делаем полезный формат: сотрудник + сколько заказов он ведёт за период + сумма.
    grouping = (grouping or "").strip().lower()

    orders_q = Q()
    if period_from:
        orders_q &= Q(orders__date__gte=period_from)
    if period_to:
        orders_q &= Q(orders__date__lte=period_to)

    if grouping in ("", "none"):
        qs = (
            Employee.objects
            .annotate(
                orders_count=Count("orders", filter=orders_q, distinct=True),
                amount_total_sum=Sum("orders__amount_total", filter=orders_q),
            )
            .order_by("full_name")
        )
        columns = [
            "full_name", "tab_number", "position", "department", "status",
            "orders_count", "amount_total_sum",
        ]
        rows = []
        for e in qs:
            rows.append({
                "full_name": e.full_name,
                "tab_number": e.tab_number,
                "position": e.position,
                "department": e.department,
                "status": e.status,
                "orders_count": e.orders_count or 0,
                "amount_total_sum": str(e.amount_total_sum or 0),
            })
        return columns, rows

    # Если хотите — можно расширить: grouping=department
    if grouping == "department":
        qs = (
            Employee.objects
            .values("department")
            .annotate(
                employees_count=Count("id"),
                orders_count=Count("orders", filter=orders_q, distinct=True),
                amount_total_sum=Sum("orders__amount_total", filter=orders_q),
            )
            .order_by("department")
        )
        columns = ["department", "employees_count", "orders_count", "amount_total_sum"]
        rows = []
        for r in qs:
            rows.append({
                "department": r["department"],
                "employees_count": r["employees_count"],
                "orders_count": r["orders_count"],
                "amount_total_sum": str(r["amount_total_sum"] or 0),
            })
        return columns, rows

    raise ValueError("Неверная группировка для отчёта по сотрудникам")


def build_finance_report(period_from, period_to, grouping: str):
    # Финансы считаем из заказов (amount_total). Если будет отдельная фин.таблица — заменим.
    grouping = (grouping or "").strip().lower()

    if grouping in ("", "none"):
        columns = ["date", "number", "client", "manager", "amount_total"]
        rows = []
        for o in _orders_queryset(period_from, period_to):
            rows.append({
                "date": o.date.isoformat() if o.date else "",
                "number": o.number,
                "client": str(o.client),
                "manager": str(o.manager),
                "amount_total": str(o.amount_total),
            })
        return columns, rows

    if grouping == "client":
        qs = (
            Order.objects
            .filter(_order_period_q(period_from, period_to))
            .values("client__name")
            .annotate(
                orders_count=Count("id"),
                amount_total_sum=Sum("amount_total"),
            )
            .order_by("client__name")
        )
        columns = ["client", "orders_count", "amount_total_sum"]
        rows = []
        for r in qs:
            rows.append({
                "client": r["client__name"],
                "orders_count": r["orders_count"],
                "amount_total_sum": str(r["amount_total_sum"] or 0),
            })
        return columns, rows

    if grouping == "manager":
        qs = (
            Order.objects
            .filter(_order_period_q(period_from, period_to))
            .values("manager__full_name")
            .annotate(
                orders_count=Count("id"),
                amount_total_sum=Sum("amount_total"),
            )
            .order_by("manager__full_name")
        )
        columns = ["manager", "orders_count", "amount_total_sum"]
        rows = []
        for r in qs:
            rows.append({
                "manager": r["manager__full_name"],
                "orders_count": r["orders_count"],
                "amount_total_sum": str(r["amount_total_sum"] or 0),
            })
        return columns, rows

    raise ValueError("Неверная группировка для финансового отчёта")


def build_report_data(report_type: str, period_from, period_to, grouping: str):
    report_type = (report_type or "").strip().lower()
    grouping = (grouping or "").strip().lower()

    if grouping not in GROUPING_VALUES and not (report_type == "employees" and grouping == "department"):
        raise ValueError("Неверное значение grouping")

    if report_type == "orders":
        return build_orders_report(period_from, period_to, grouping)

    if report_type == "employees":
        return build_employees_report(period_from, period_to, grouping)

    if report_type == "finance":
        return build_finance_report(period_from, period_to, grouping)

    raise ValueError("Неверный report_type")


def render_csv_bytes(columns, rows):
    # UTF-8 with BOM — чтобы Excel открывал нормально
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue().encode("utf-8-sig")
