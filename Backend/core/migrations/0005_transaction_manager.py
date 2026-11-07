import django.db.models.deletion
from django.db import migrations, models


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
        # Pisahkan ADD COLUMN dan ADD FOREIGN KEY agar kompatibel dengan TiDB.
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE `core_transaction` ADD COLUMN `manager_id` bigint NULL',
                    reverse_sql='ALTER TABLE `core_transaction` DROP COLUMN `manager_id`',
                ),
                migrations.RunSQL(
                    sql=(
                        'ALTER TABLE `core_transaction` '
                        'ADD CONSTRAINT `core_transaction_manager_id_d830aa88_fk_core_employee_id` '
                        'FOREIGN KEY (`manager_id`) REFERENCES `core_employee` (`id`)'
                    ),
                    reverse_sql=(
                        'ALTER TABLE `core_transaction` '
                        'DROP FOREIGN KEY `core_transaction_manager_id_d830aa88_fk_core_employee_id`'
                    ),
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='transaction',
                    name='manager',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='restaurant_transactions',
                        to='core.employee',
                    ),
                ),
            ],
        ),
    ]
