# Generated by Django 4.1.5 on 2023-02-16 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkings', '0002_alter_price_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='day',
            field=models.CharField(max_length=15, null=True),
        ),
    ]