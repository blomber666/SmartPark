# Generated by Django 4.1.5 on 2023-01-27 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkings', '0004_price_statistic_rename_stop_id_payment_stop_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='user',
            field=models.CharField(max_length=50),
        ),
    ]
