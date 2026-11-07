from django.conf import settings
from rest_framework import serializers
from .models import Employee, Shift, Transaction, TransactionItem, Product

CATEGORIES = ['Makanan berat', 'Pembuka', 'Penutup', 'Pendamping', 'Minuman']
MAX_PRICE = 100_000_000


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

class TransactionLineSerializer(serializers.ModelSerializer):
    # Nama & harga adalah snapshot saat transaksi, jadi tetap benar walau menu diubah/dihapus.
    unitPrice = serializers.IntegerField(source='unit_price')
    class Meta:
        model = TransactionItem
        fields = ['name','unitPrice','quantity']

class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    cashierId = serializers.SerializerMethodField()
    shiftId = serializers.SerializerMethodField()
    orderType = serializers.CharField(source='order_type')
    guestCount = serializers.IntegerField(source='guest_count', read_only=True, allow_null=True)
    lines = serializers.SerializerMethodField()
    class Meta:
        model = Transaction
        fields = ['id','number','cashierId','shiftId','at','items','subtotal','discount','tax','total','orderType','guestCount','lines']
    def get_id(self,obj): return str(obj.pk)
    def get_cashierId(self,obj): return str(obj.cashier_id)
    def get_shiftId(self,obj): return str(obj.shift_id)
    def get_lines(self,obj):
        # sorted() di Python (bukan order_by) supaya memakai hasil prefetch_related dan tidak menambah query per transaksi.
        return TransactionLineSerializer(sorted(obj.lines.all(), key=lambda line: line.pk), many=True).data

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','description','price','category','image','tag','active']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 1:
            raise serializers.ValidationError('Nama menu wajib diisi.')
        return value

    def validate_price(self, value):
        if value < 1:
            raise serializers.ValidationError('Harga harus lebih dari 0.')
        if value > MAX_PRICE:
            raise serializers.ValidationError('Harga terlalu besar.')
        return value

    def validate_category(self, value):
        if value not in CATEGORIES:
            raise serializers.ValidationError('Kategori tidak valid. Pilih: ' + ', '.join(CATEGORIES) + '.')
        return value

    def validate_image(self, value):
        if not value:
            return ''
        if not (value.startswith('data:image/') or value.startswith('https://') or value.startswith('http://')):
            raise serializers.ValidationError('Format gambar tidak valid.')
        if len(value) > settings.POS_MAX_IMAGE_CHARS:
            raise serializers.ValidationError('Gambar terlalu besar. Gunakan gambar yang lebih kecil.')
        return value
