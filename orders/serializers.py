from dataclasses import field
from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusDict, Report, Integration


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderStatusDictSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderStatusDict
        fields = "__all__"


class ReportSerializer(serializers.ModelSerializer):
    def validate_format(self, value):
        v = (value or "").upper()
        if v != "CSV":
            raise serializers.ValidationError("Сейчас поддерживается только CSV")
        return v

    def validate_grouping(self, value):
        v = (value or "").strip().lower()
        allowed = {"", "none", "client", "manager", "department"}  # department — опционально для employees
        if v not in allowed:
            raise serializers.ValidationError("Неверная группировка")
        return v
    def validate(self, attrs):
        report_type = (attrs.get("report_type") or "").strip().lower()
        grouping = (attrs.get("grouping") or "").strip().lower()

        if grouping in ("", "none"):
            grouping = "none"

        if report_type == "employees":
            allowed = {"none", "department"}
            if grouping not in allowed:
                raise serializers.ValidationError({
                    "grouping": "Для отчёта по сотрудникам доступно: Без группировки или По подразделениям"
                })
        else:
            allowed = {"none", "client", "manager"}
            if grouping not in allowed:
                raise serializers.ValidationError({
                    "grouping": "Доступные группировки: Без группировки / По клиентам / По менеджерам"
                })

        return attrs

    class Meta:
        model = Report
        fields = "__all__"


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = "__all__"
