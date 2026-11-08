import django.db.models.deletion
from django.db import migrations, models

from ._tidb_compat import AddNullableForeignKeySplit


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_transaction_guest_count'),
    ]

    operations = [
        # MySQL/TiDB: ADD COLUMN dan ADD FOREIGN KEY dipisah (TiDB). Database lain (SQLite untuk tes/CI): AddField standar.
        AddNullableForeignKeySplit(
            model_name='product',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='products',
                to='core.employee',
            ),
            fk_name='core_product_owner_id_fk_core_employee_id',
        ),
    ]
