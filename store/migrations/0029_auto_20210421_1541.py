# Generated by Django 3.1.5 on 2021-04-21 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_auto_20210421_1434'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='password',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='phone',
        ),
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
