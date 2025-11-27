from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from .models import Role, User, Employee, Client
from .serializers import RoleSerializer, EmployeeSerializer, ClientSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department", "status", "user__role__name"]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        # Заглушка: инициировать workflow сброса пароля
        return Response({"status": "password reset requested"})

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        emp = self.get_object()
        if emp.user:
            emp.user.is_active_account = False
            emp.user.save()
        emp.status = "Деактивирован"
        emp.save()
        return Response({"status": "deactivated"})


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]
    permission_classes = [permissions.IsAuthenticated]
