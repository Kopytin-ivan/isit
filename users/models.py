from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)
    can_view_orders = models.BooleanField(default=True)
    can_edit_orders = models.BooleanField(default=False)
    can_delete_orders = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name


class User(AbstractUser):
    role = models.ForeignKey(Role, null=True, on_delete=models.SET_NULL)
    is_active_account = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Employee(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    full_name = models.CharField(max_length=255)
    tab_number = models.CharField(max_length=32, unique=True)
    position = models.CharField(max_length=128)
    department = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    status = models.CharField(max_length=64, default="Активен")

    class Meta:
        verbose_name = " Работник"
        verbose_name_plural = "Работники"

    def __str__(self):
        return self.full_name


class Client(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.name
