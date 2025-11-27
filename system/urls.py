"""
URL configuration for system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import path

# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import RoleViewSet, EmployeeViewSet, ClientViewSet
from orders.views import (
    OrderViewSet,
    OrderItemViewSet,
    ReportViewSet,
    IntegrationViewSet,
    OrderStatusDictViewSet,
)


router = DefaultRouter()
router.register(r"roles", RoleViewSet)
router.register(r"employees", EmployeeViewSet)
router.register(r"clients", ClientViewSet)
router.register(r"orders", OrderViewSet)
router.register(r"order-items", OrderItemViewSet)
router.register(r"reports", ReportViewSet)
router.register(r"integrations", IntegrationViewSet)
router.register(r"dictionaries/order-statuses", OrderStatusDictViewSet)

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path("api/v1/auth/", include("djoser.urls")),
]

