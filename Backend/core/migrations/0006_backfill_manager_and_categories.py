from django.db import migrations

CATEGORY_MAP = {
    'Burger': 'Makanan berat',
    'Pizza': 'Makanan berat',
    'Mangkok': 'Makanan berat',
    'Taco': 'Pembuka',
}
VALID = {'Makanan berat', 'Pembuka', 'Penutup', 'Pendamping', 'Minuman'}


def backfill(apps, schema_editor):
    Employee = apps.get_model('core', 'Employee')
    Transaction = apps.get_model('core', 'Transaction')
    Product = apps.get_model('core', 'Product')

    # Transaksi lama: manajer = manajer yang mendaftarkan kasirnya. Nomor lama TIDAK diubah.
    for cashier in Employee.objects.filter(role='cashier'):
        Transaction.objects.filter(cashier=cashier, manager__isnull=True).update(manager_id=cashier.created_by_id)
    for manager in Employee.objects.filter(role='manager'):
        Transaction.objects.filter(cashier=manager, manager__isnull=True).update(manager_id=manager.pk)

    # Kategori lama -> kategori baru.
    for old, new in CATEGORY_MAP.items():
        Product.objects.filter(category=old).update(category=new)
    Product.objects.exclude(category__in=VALID).update(category='Makanan berat')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_transaction_manager'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
