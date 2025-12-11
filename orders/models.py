#orders/models.py
from django.db import models

from users.models import Client, Employee


class Order(models.Model):
    STATUS = [
        ("new", "Новый"),
        ("ready", "Готов"),
        ("canceled", "Отменён"),
    ]

    number = models.CharField(max_length=32, unique=True)
    date = models.DateField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    department = models.CharField(max_length=128)
    manager = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="orders"
    )
    status = models.CharField(
        max_length=64, choices=STATUS, default="new"
    )  # Новый, В работе, Выполнен, Отменён
    priority = models.CharField(
        max_length=32, default="Обычный"
    )  # Низкий/Обычный/Высокий
    order_type = models.CharField(max_length=64, default="Поставка оборудования")
    planned_date = models.DateField(null=True, blank=True)
    amount_total = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Номер: {self.number}, клиент: {self.client}, дата: {self.date} "


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    qty = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.CharField(max_length=32, default="шт")
    price = models.DecimalField(max_digits=16, decimal_places=2)
    amount = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name


class Report(models.Model):
    REPORT_TYPES = [
        ("orders", "По заказам"),
        ("employees", "По сотрудникам"),
        ("finance", "Финансовый"),
    ]
    STATUS = [("ready", "Готов"), ("processing", "В процессе"), ("error", "Ошибка")]
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=32, choices=REPORT_TYPES)
    period_from = models.DateField(null=True, blank=True)
    period_to = models.DateField(null=True, blank=True)
    format = models.CharField(max_length=16, default="PDF")
    grouping = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=16, choices=STATUS, default="processing")
    file = models.FileField(upload_to="reports/", null=True, blank=True)
    params = models.JSONField(default=dict, blank=True)
    recipient_email = models.EmailField(blank=True)

    class Meta:
        verbose_name = "Отчёт"
        verbose_name_plural = "Отчёты"

    def __str__(self):
        return self.title


class Integration(models.Model):
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64)  # ERP, HR, etc.
    status = models.CharField(max_length=64, default="Активна")
    last_exchange = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Интеграция"
        verbose_name_plural = "Интеграции"

    def __str__(self):
        return self.name


class OrderStatusDict(models.Model):
    value = models.CharField(max_length=64, unique=True)
    display = models.CharField(max_length=64)

    class Meta:
        verbose_name = "Словарь заказ и статуса"
        verbose_name_plural = "Словарь заказов и статусов"

    def __str__(self):
        return self.value + self.display
