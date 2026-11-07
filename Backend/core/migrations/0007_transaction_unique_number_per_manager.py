from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_backfill_manager_and_categories'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='transaction',
            constraint=models.UniqueConstraint(fields=('manager', 'number'), name='unique_order_number_per_manager'),
        ),
    ]
