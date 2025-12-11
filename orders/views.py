#orders/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

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
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["order"]


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["report_type", "status", "period_from", "period_to"]

    @action(detail=True, methods=["post"])
    def generate(self, request, pk=None):
        report = self.get_object()
        report.status = "ready"
        report.save()
        return Response({"status": "ready"})

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        # Вернуть файл или ссылку
        return Response({"url": f"/media/{self.get_object().file}"})


class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



class OrderStatusDictViewSet(viewsets.ModelViewSet):
    queryset = OrderStatusDict.objects.all()
    serializer_class = OrderStatusDictSerializer
    permission_classes = [permissions.IsAdminUser]
