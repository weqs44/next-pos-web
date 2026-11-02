from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employee, Shift, Transaction, Product

class AccountSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField(source='user.first_name')
    email = serializers.EmailField(source='user.email')
    createdAt = serializers.IntegerField(source='created_at')
    createdBy = serializers.SerializerMethodField()
    class Meta:
        model = Employee
        fields = ['id','name','email','title','role','active','createdAt','createdBy']
    def get_id(self,obj): return str(obj.pk)
    def get_createdBy(self,obj): return str(obj.created_by_id) if obj.created_by_id else None

class ShiftSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    cashierId = serializers.SerializerMethodField()
    startedAt = serializers.IntegerField(source='started_at')
    endedAt = serializers.IntegerField(source='ended_at')
    class Meta:
        model = Shift
        fields = ['id','cashierId','startedAt','endedAt']
    def get_id(self,obj): return str(obj.pk)
    def get_cashierId(self,obj): return str(obj.cashier_id)

class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    cashierId = serializers.SerializerMethodField()
    shiftId = serializers.SerializerMethodField()
    orderType = serializers.CharField(source='order_type')
    guestCount = serializers.IntegerField(source='guest_count', read_only=True, allow_null=True)
    class Meta:
        model = Transaction
        fields = ['id','number','cashierId','shiftId','at','items','subtotal','discount','tax','total','orderType','guestCount']
    def get_id(self,obj): return str(obj.pk)
    def get_cashierId(self,obj): return str(obj.cashier_id)
    def get_shiftId(self,obj): return str(obj.shift_id)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','description','price','category','image','tag','active']
