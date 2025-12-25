#orders/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import OrderAccessPermission, ReportAccessPermission
from .reporting import build_report_data, render_csv_bytes
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.utils.text import slugify
from django.utils import timezone

from .models import Order, OrderItem, OrderStatusDict, Report, Integration
from .serializers import (
    OrderItemSerializer,
    OrderSerializer,
    ReportSerializer,
    IntegrationSerializer,
    OrderStatusDictSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = (
        Order.objects.select_related("client", "manager")
        .prefetch_related("items")
        .all()
    )
    permission_classes = [OrderAccessPermission]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "status",
        "priority",
        "order_type",
        "manager",
        "client",
        "department",
        "date",
    ]

    @action(detail=True, methods=["post"])
    def reserve(self, request, pk=None):
        order = self.get_object()
        order.status = "new"      # или "ready"/"in_progress" если придумаешь код
        order.save()
        return Response({"status": order.status})

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        order = self.get_object()
        order.status = "ready"
        order.save()
        return Response({"status": order.status})

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        order.status = "canceled"
        order.save()
        return Response({"status": order.status})



class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [OrderAccessPermission]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["order"]


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by("-id")
    serializer_class = ReportSerializer
    permission_classes = [ReportAccessPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["report_type", "status", "period_from", "period_to", "format", "grouping"]

    def perform_create(self, serializer):
        report = serializer.save(status="processing")

        # генерируем синхронно (очередь сделаем позже)
        try:
            self._generate_csv(report)
        except Exception as e:
            report.status = "error"
            report.params = {**(report.params or {}), "error": str(e)}
            report.save(update_fields=["status", "params"])

    def _generate_csv(self, report: Report):
        fmt = (report.format or "").upper()
        if fmt != "CSV":
            raise ValueError("Сейчас поддерживается только формат CSV")

        grouping = self._normalize_grouping(report.report_type, report.grouping)

        # сохраним нормализованное значение, чтобы дальше не падало
        if report.grouping != grouping:
            report.grouping = grouping
            report.save(update_fields=["grouping"])

        columns, rows = build_report_data(
            report_type=report.report_type,
            period_from=report.period_from,
            period_to=report.period_to,
            grouping=grouping,
        )


        csv_bytes = render_csv_bytes(columns, rows)

        # имя файла
        dt = timezone.now().strftime("%Y%m%d_%H%M%S")
        safe_title = slugify(report.title) or f"report_{report.id}"
        filename = f"{safe_title}_{dt}.csv"

        report.file.save(filename, ContentFile(csv_bytes), save=False)
        report.status = "ready"
        report.params = {
            **(report.params or {}),
            "columns": columns,
            "rows_count": len(rows),
        }
        report.save(update_fields=["file", "status", "params"])
    def _normalize_grouping(self, report_type: str, grouping: str) -> str:
        """
        Нормализуем старые/текстовые значения grouping:
        - "по клиентам" -> client
        - "по менеджерам" -> manager
        - "по подразделениям" -> department
        - для employees client/manager принудительно превращаем в none
        """
        rt = (report_type or "").strip().lower()
        g = (grouping or "").strip().lower()

        if g in ("", "none"):
            g = "none"

        # русские/свободные формулировки (на случай старых записей)
        if "клиент" in g:
            g = "client"
        elif "менедж" in g:
            g = "manager"
        elif "подраз" in g:
            g = "department"

        # отчёт по сотрудникам не поддерживает client/manager
        if rt == "employees" and g in ("client", "manager"):
            g = "none"

        return g

    @action(detail=True, methods=["post"])
    def generate(self, request, pk=None):
        report = self.get_object()
        try:
            self._generate_csv(report)
        except Exception as e:
            report.status = "error"
            report.params = {**(report.params or {}), "error": str(e)}
            report.save(update_fields=["status", "params"])
            return Response({"status": "error", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "ready"})

    @action(detail=True, methods=["get"])
    def preview(self, request, pk=None):
        report = self.get_object()

        # если не готов — попробуем сгенерить
        if report.status != "ready" or not report.file:
            try:
                self._generate_csv(report)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # preview берём из сохранённого CSV (первые N строк)
        limit = int(request.query_params.get("limit", 200))

        report.file.open("rb")
        data = report.file.read().decode("utf-8-sig").splitlines()
        report.file.close()

        import csv
        reader = csv.DictReader(data)
        rows = []
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(row)

        return Response({
            "title": report.title,
            "report_type": report.report_type,
            "format": report.format,
            "grouping": report.grouping,
            "period_from": report.period_from,
            "period_to": report.period_to,
            "columns": reader.fieldnames or [],
            "rows": rows,
            "rows_count": (report.params or {}).get("rows_count"),
        })

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        report = self.get_object()

        if report.status != "ready" or not report.file:
            try:
                self._generate_csv(report)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        report.file.open("rb")
        resp = FileResponse(report.file, content_type="text/csv")
        resp["Content-Disposition"] = f'attachment; filename="{report.file.name.split("/")[-1]}"'
        return resp



class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



class OrderStatusDictViewSet(viewsets.ModelViewSet):
    queryset = OrderStatusDict.objects.all()
    serializer_class = OrderStatusDictSerializer
    permission_classes = [permissions.IsAdminUser]
