# Generated by Django 3.1.5 on 2021-04-20 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_auto_20210420_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
