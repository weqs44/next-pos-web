from django.conf import settings
from django.db import models

class Employee(models.Model):
    ROLE_CHOICES = [('manager','manager'),('cashier','cashier')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee')
    title = models.CharField(max_length=120, default='Kasir')
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default='cashier')
    active = models.BooleanField(default=True)
    created_at = models.BigIntegerField()
    created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_employees')
    def __str__(self): return self.user.email

class Shift(models.Model):
    cashier = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='shifts')
    started_at = models.BigIntegerField()
    ended_at = models.BigIntegerField(null=True, blank=True)

class Transaction(models.Model):
    number = models.PositiveIntegerField(unique=True)
    cashier = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='transactions')
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, related_name='transactions')
    at = models.BigIntegerField()
    items = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField(default=0)
    tax = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField()
    order_type = models.CharField(max_length=40)
    guest_count = models.PositiveIntegerField(null=True, blank=True, default=None)

class Product(models.Model):
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=300, blank=True, default='')
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=80)
    image = models.TextField(blank=True, default='')
    tag = models.CharField(max_length=80, blank=True, default='')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
