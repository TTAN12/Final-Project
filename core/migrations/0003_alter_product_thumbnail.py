# Generated by Django 5.0.7 on 2024-12-09 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_product_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='thumbnail',
            field=models.ImageField(upload_to=''),
        ),
    ]
