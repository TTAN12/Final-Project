# Generated by Django 5.0.7 on 2024-12-09 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_order_orderitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total_price',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='price',
        ),
    ]
