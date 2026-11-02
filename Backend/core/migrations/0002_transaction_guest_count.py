# Adds an optional guest count without changing existing transaction records.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='guest_count',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]
