# users/views.py
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Role, Employee, Client
from .serializers import RoleSerializer, EmployeeSerializer, ClientSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.AllowAny]  # чтение без логина
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    # Для учебного прототипа разрешим изменения всем
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department", "status"]


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.AllowAny]  # вместо IsAuthenticatedOrReadOnly
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]
