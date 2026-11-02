import time
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from django.db.models import Max
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Employee, Shift, Transaction, Product
from .serializers import AccountSerializer, ShiftSerializer, TransactionSerializer, ProductSerializer

MENU = [
 {'name':'Menu 1','description':'Gurih banget','price':69000,'category':'Burger','image':'https://images.unsplash.com/photo-1575367439051-9be800a160d8?auto=format&fit=crop&w=900&q=85','tag':'Terlaris'},
 {'name':'Menu 2','description':'Mama mia','price':58000,'category':'Pizza','image':'https://images.unsplash.com/photo-1624340209361-bfad6e30dbf4?auto=format&fit=crop&w=900&q=85','tag':'Klasik'},
 {'name':'Menu 3','description':'Sehat banget','price':55000,'category':'Mangkok','image':'https://images.unsplash.com/photo-1653026645442-5dae0f5b9090?auto=format&fit=crop&w=900&q=85','tag':'Nabati'},
 {'name':'Menu 4','description':'Lezatos','price':72000,'category':'Pizza','image':'https://images.unsplash.com/photo-1622257892554-c162e47a3a5e?auto=format&fit=crop&w=900&q=85','tag':'Baru'},
 {'name':'Menu 5','description':'Hola como estas','price':64000,'category':'Taco','image':'https://images.unsplash.com/photo-1643757343278-5d50309dfa44?auto=format&fit=crop&w=900&q=85','tag':'Pilihan koki'},
 {'name':'Menu 6','description':'Seger banget','price':32000,'category':'Minuman','image':'https://images.unsplash.com/photo-1756572323135-d242095298ec?auto=format&fit=crop&w=900&q=85','tag':'Tanpa alkohol'},
 {'name':'Menu 7','description':'Kenyang banget','price':85000,'category':'Pendamping','image':'https://images.unsplash.com/photo-1733159680303-1bd3875eb71b?auto=format&fit=crop&w=900&q=85','tag':'Terbatas'},
 {'name':'Menu 8','description':'Rame banget','price':76000,'category':'Pizza','image':'https://images.unsplash.com/photo-1659367736714-e3f0344a6266?auto=format&fit=crop&w=900&q=85','tag':'Untuk berbagi'},
]

def account_data(employee): return AccountSerializer(employee).data
def error(message, code=400): return Response({'error': message}, status=code)
def employee_for(user):
    try: return user.employee
    except Employee.DoesNotExist: return None

def require_manager(request):
    actor = employee_for(request.user)
    if not actor or actor.role != 'manager' or not actor.active: return None
    return actor

class HealthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def get(self, request): return Response({'status':'ok','service':'NEXT POS API'})

class RegisterManagerView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        name = str(request.data.get('name','')).strip(); email = str(request.data.get('email','')).strip().lower(); password = str(request.data.get('password',''))
        if len(name)<2: return error('Nama lengkap minimal 2 karakter.')
        if '@' not in email or '.' not in email.split('@')[-1]: return error('Masukkan alamat email yang valid.')
        if len(password)<6: return error('Kata sandi minimal 6 karakter.')
        if User.objects.filter(username=email).exists(): return error('Email ini sudah terdaftar. Silakan masuk.')
        user = User.objects.create_user(username=email,email=email,password=password,first_name=name)
        employee = Employee.objects.create(user=user,title='Manajer toko',role='manager',active=True,created_at=int(time.time()*1000))
        token,_ = Token.objects.get_or_create(user=user)
        return Response({'account':account_data(employee),'token':token.key},status=201)

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        email = str(request.data.get('email','')).strip().lower(); password = str(request.data.get('password',''))
        if '@' not in email: return error('Masukkan alamat email yang valid.')
        user = authenticate(request,username=email,password=password)
        if not user: return error('Email atau kata sandi salah.',401)
        employee = employee_for(user)
        if not employee: return error('Akun tidak memiliki profil pekerja.',403)
        if not employee.active: return error('Akun ini dinonaktifkan. Hubungi manajer Anda.',403)
        token,_ = Token.objects.get_or_create(user=user)
        return Response({'account':account_data(employee),'token':token.key})

class LogoutView(APIView):
    def post(self, request):
        request.auth.delete()
        return Response({'ok':True})

class BootstrapView(APIView):
    def get(self, request):
        me = employee_for(request.user)
        if not me or not me.active: return error('Akun tidak aktif.',403)
        cashiers = Employee.objects.filter(role='cashier').select_related('user').order_by('id')
        shifts = Shift.objects.all().order_by('-started_at')
        transactions = Transaction.objects.all().order_by('-at')
        if me.role == 'cashier':
            shifts = shifts.filter(cashier=me); transactions = transactions.filter(cashier=me)
        return Response({'account':account_data(me),'cashiers':AccountSerializer(cashiers,many=True).data,'shifts':ShiftSerializer(shifts,many=True).data,'transactions':TransactionSerializer(transactions[:5000],many=True).data,'products':ProductSerializer(Product.objects.all().order_by('id'),many=True).data})

class ProfileView(APIView):
    def patch(self, request):
        employee = employee_for(request.user)
        if not employee: return error('Akun tidak ditemukan.',404)
        name = str(request.data.get('name','')).strip(); title = str(request.data.get('title','')).strip()
        if len(name)<2: return error('Nama lengkap minimal 2 karakter.')
        employee.user.first_name=name; employee.user.save(update_fields=['first_name'])
        if title: employee.title=title
        employee.save()
        return Response(account_data(employee))

class CashierCollectionView(APIView):
    def post(self, request):
        actor=require_manager(request)
        if not actor: return error('Hanya manajer yang dapat mendaftarkan kasir.',403)
        name=str(request.data.get('name','')).strip(); email=str(request.data.get('email','')).strip().lower(); password=str(request.data.get('password','')); title=str(request.data.get('title','Kasir')).strip() or 'Kasir'
        if len(name)<2: return error('Nama lengkap minimal 2 karakter.')
        if '@' not in email or '.' not in email.split('@')[-1]: return error('Masukkan alamat email yang valid.')
        if len(password)<6: return error('Kata sandi minimal 6 karakter.')
        if User.objects.filter(username=email).exists(): return error('Email ini sudah terdaftar.')
        user=User.objects.create_user(username=email,email=email,password=password,first_name=name)
        employee=Employee.objects.create(user=user,title=title,role='cashier',active=True,created_at=int(time.time()*1000),created_by=actor)
        return Response(account_data(employee),status=201)
    def patch(self, request):
        actor=require_manager(request)
        if not actor: return error('Hanya manajer yang dapat mengubah status kasir.',403)
        target=Employee.objects.filter(pk=request.data.get('id'),role='cashier').first()
        if not target: return error('Kasir tidak ditemukan.',404)
        target.active=bool(request.data.get('active')); target.save(update_fields=['active'])
        if not target.active: Shift.objects.filter(cashier=target,ended_at__isnull=True).update(ended_at=int(time.time()*1000))
        return Response({'ok':True})

class CashierPasswordView(APIView):
    def post(self, request):
        if not require_manager(request): return error('Hanya manajer yang dapat mengatur ulang kata sandi.',403)
        target=Employee.objects.filter(pk=request.data.get('id'),role='cashier').select_related('user').first()
        password=str(request.data.get('password',''))
        if not target: return error('Kasir tidak ditemukan.',404)
        if len(password)<6: return error('Kata sandi minimal 6 karakter.')
        target.user.set_password(password); target.user.save()
        Token.objects.filter(user=target.user).delete()
        return Response({'ok':True})

class ShiftView(APIView):
    def post(self, request):
        employee=employee_for(request.user)
        if not employee or employee.role!='cashier' or not employee.active: return error('Hanya kasir aktif yang dapat mengelola shift.',403)
        action=request.data.get('action'); now=int(time.time()*1000)
        opened=Shift.objects.filter(cashier=employee,ended_at__isnull=True).first()
        if action=='start':
            if opened and now-opened.started_at < 14*3600000: shift=opened
            else:
                if opened: opened.ended_at=opened.started_at+14*3600000; opened.save(update_fields=['ended_at'])
                shift=Shift.objects.create(cashier=employee,started_at=now)
        elif action=='end':
            if opened: opened.ended_at=now; opened.save(update_fields=['ended_at']); shift=opened
            else: return error('Tidak ada shift aktif.',409)
        else: return error('Aksi shift tidak valid.')
        return Response(ShiftSerializer(shift).data)

class TransactionView(APIView):
    def post(self, request):
        employee=employee_for(request.user)
        if not employee or employee.role!='cashier' or not employee.active: return error('Hanya kasir aktif yang dapat memproses transaksi.',403)
        shift=Shift.objects.filter(cashier=employee,ended_at__isnull=True).first()
        if not shift: return error('Aktifkan shift terlebih dahulu sebelum memproses pembayaran.',409)
        try:
            items=int(request.data.get('items',0)); subtotal=int(round(float(request.data.get('subtotal',0)))); discount=int(round(float(request.data.get('discount',0)))); tax=int(round(float(request.data.get('tax',0))))
        except (TypeError,ValueError): return error('Nilai transaksi tidak valid.')
        if items<1 or subtotal<0 or discount<0 or discount>subtotal or tax<0: return error('Nilai transaksi tidak valid.')
        order_type=str(request.data.get('orderType','Makan di tempat'))[:40]
        guest_count_raw=request.data.get('guestCount')
        try:
            if isinstance(guest_count_raw, float) and not guest_count_raw.is_integer():
                raise ValueError
            guest_count=None if guest_count_raw in (None, '') else int(guest_count_raw)
        except (TypeError,ValueError):
            return error('Jumlah tamu tidak valid.')
        if order_type == 'Makan di tempat' and guest_count is None:
            return error('Jumlah tamu wajib dikirim untuk pesanan makan di tempat.')
        if guest_count is not None and guest_count<1:
            return error('Jumlah tamu minimal 1.')
        if order_type != 'Makan di tempat':
            guest_count=None
        with db_transaction.atomic():
            number=(Transaction.objects.aggregate(m=Max('number'))['m'] or 0)+1
            tx=Transaction.objects.create(number=number,cashier=employee,shift=shift,at=int(time.time()*1000),items=items,subtotal=subtotal,discount=discount,tax=tax,total=subtotal-discount+tax,order_type=order_type,guest_count=guest_count)
        return Response(TransactionSerializer(tx).data,status=201)

class ProductCollectionView(APIView):
    def get(self, request): return Response(ProductSerializer(Product.objects.all().order_by('id'),many=True).data)
    def post(self, request):
        actor=employee_for(request.user)
        if not actor or actor.role!='manager': return error('Hanya manajer yang dapat mengelola menu.',403)
        serializer=ProductSerializer(data=request.data)
        if not serializer.is_valid(): return Response(serializer.errors,status=400)
        serializer.save(); return Response(serializer.data,status=201)
    def patch(self, request):
        actor=employee_for(request.user)
        if not actor or actor.role!='manager': return error('Hanya manajer yang dapat mengelola menu.',403)
        product=Product.objects.filter(pk=request.data.get('id')).first()
        if not product: return error('Menu tidak ditemukan.',404)
        if 'active' in request.data: product.active=bool(request.data['active'])
        for key in ['name','description','price','category','image','tag']:
            if key in request.data: setattr(product,key,request.data[key])
        product.save(); return Response(ProductSerializer(product).data)
    def delete(self, request):
        actor=employee_for(request.user)
        if not actor or actor.role!='manager': return error('Hanya manajer yang dapat mengelola menu.',403)
        product=Product.objects.filter(pk=request.data.get('id')).first()
        if not product: return error('Menu tidak ditemukan.',404)
        product.delete(); return Response({'ok':True})

