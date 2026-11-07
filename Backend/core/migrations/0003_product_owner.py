import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_transaction_guest_count'),
    ]

    operations = [
        # Pisahkan ADD COLUMN dan ADD FOREIGN KEY agar kompatibel dengan TiDB.
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE `core_product` ADD COLUMN `owner_id` bigint NULL',
                    reverse_sql='ALTER TABLE `core_product` DROP COLUMN `owner_id`',
                ),
                migrations.RunSQL(
                    sql=(
                        'ALTER TABLE `core_product` '
                        'ADD CONSTRAINT `core_product_owner_id_fk_core_employee_id` '
                        'FOREIGN KEY (`owner_id`) REFERENCES `core_employee` (`id`)'
                    ),
                    reverse_sql=(
                        'ALTER TABLE `core_product` '
                        'DROP FOREIGN KEY `core_product_owner_id_fk_core_employee_id`'
                    ),
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='product',
                    name='owner',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='products',
                        to='core.employee',
                    ),
                ),
            ],
        ),
    ]
