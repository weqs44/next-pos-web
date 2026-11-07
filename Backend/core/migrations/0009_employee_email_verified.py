from django.db import migrations, models


def mark_existing_verified(apps, schema_editor):
    # Akun yang sudah ada sebelum fitur ini tetap bisa masuk tanpa verifikasi.
    apps.get_model('core', 'Employee').objects.update(email_verified=True)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_transactionitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(mark_existing_verified, migrations.RunPython.noop),
    ]
