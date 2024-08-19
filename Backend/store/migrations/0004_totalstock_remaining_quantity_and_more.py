# Generated by Django 5.0.1 on 2024-08-19 15:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_remove_totalstock_remaining_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='totalstock',
            name='remaining_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='totalstock',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product'),
        ),
    ]
