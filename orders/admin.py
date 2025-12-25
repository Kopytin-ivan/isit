from django.contrib import admin

from .models import Order, OrderItem, OrderStatusDict
from .models import Order, OrderItem, OrderStatusDict, Report

admin.site.site_header = "Админ панель"

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderStatusDict)
admin.site.register(Report)