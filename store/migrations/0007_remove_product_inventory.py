# Generated by Django 3.1.5 on 2021-04-06 06:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_product_inventory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='inventory',
        ),
    ]
