from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_employee_email_verified'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='employee',
            index=models.Index(fields=['created_by', 'role'], name='emp_creator_role_idx'),
        ),
        migrations.AddIndex(
            model_name='shift',
            index=models.Index(fields=['cashier', 'started_at'], name='shift_cashier_started_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['manager', 'at'], name='tx_manager_at_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['cashier', 'at'], name='tx_cashier_at_idx'),
        ),
    ]
