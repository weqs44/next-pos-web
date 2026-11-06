from django.db import migrations


def split_menu(apps, schema_editor):
    # Menu lama dipakai bersama semua restoran. Pisahkan: manajer pertama memegang menu aslinya,
    # manajer lain mendapat salinan, sehingga tiap restoran punya menu sendiri (dan bisa diubah mandiri).
    Employee = apps.get_model('core', 'Employee')
    Product = apps.get_model('core', 'Product')
    managers = list(Employee.objects.filter(role='manager').order_by('id'))
    shared = list(Product.objects.filter(owner__isnull=True).order_by('id'))
    if not managers or not shared:
        return
    first, others = managers[0], managers[1:]
    for p in shared:
        for m in others:
            Product.objects.create(owner=m, name=p.name, description=p.description, price=p.price,
                                   category=p.category, image=p.image, tag=p.tag, active=p.active)
    Product.objects.filter(pk__in=[p.pk for p in shared]).update(owner=first)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_product_owner'),
    ]

    operations = [
        migrations.RunPython(split_menu, migrations.RunPython.noop),
    ]
