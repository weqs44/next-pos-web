import django.db.models.deletion
from django.db import migrations, models

from ._tidb_compat import AddNullableForeignKeySplit


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_split_shared_menu'),
    ]

    operations = [
        # Nomor tidak lagi unik secara global, tapi unik per manajer (constraint ditambahkan di 0007).
        migrations.AlterField(
            model_name='transaction',
            name='number',
            field=models.PositiveIntegerField(),
        ),
        # MySQL/TiDB: ADD COLUMN dan ADD FOREIGN KEY dipisah (TiDB). Database lain (SQLite untuk tes/CI): AddField standar.
        AddNullableForeignKeySplit(
            model_name='transaction',
            name='manager',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='restaurant_transactions',
                to='core.employee',
            ),
            fk_name='core_transaction_manager_id_d830aa88_fk_core_employee_id',
        ),
    ]
