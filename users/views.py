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
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class SessionLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "Неверный логин или пароль"}, status=status.HTTP_400_BAD_REQUEST)

        if hasattr(user, "is_active_account") and not user.is_active_account:
            return Response({"detail": "Аккаунт деактивирован"}, status=status.HTTP_403_FORBIDDEN)

        login(request, user)

        role = getattr(user, "role", None)
        perms = {
            "can_view_orders": bool(getattr(role, "can_view_orders", False)),
            "can_edit_orders": bool(getattr(role, "can_edit_orders", False)),
            "can_delete_orders": bool(getattr(role, "can_delete_orders", False)),
            "can_view_reports": bool(getattr(role, "can_view_reports", False)),
            "is_admin": bool(getattr(role, "is_admin", False)),
        }

        return Response({
            "id": user.id,
            "username": user.username,
            "role": getattr(role, "name", None),
            "permissions": perms,
        })


class SessionLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "ok"})


class SessionMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", None)
        perms = {
            "can_view_orders": bool(getattr(role, "can_view_orders", False)),
            "can_edit_orders": bool(getattr(role, "can_edit_orders", False)),
            "can_delete_orders": bool(getattr(role, "can_delete_orders", False)),
            "can_view_reports": bool(getattr(role, "can_view_reports", False)),
            "is_admin": bool(getattr(role, "is_admin", False)),
        }
        return Response({
            "id": user.id,
            "username": user.username,
            "role": getattr(role, "name", None),
            "permissions": perms,
        })
