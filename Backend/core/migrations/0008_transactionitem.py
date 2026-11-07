import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_transaction_unique_number_per_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('unit_price', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField()),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.product')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='core.transaction')),
            ],
        ),
    ]
