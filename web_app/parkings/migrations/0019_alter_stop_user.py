# Generated by Django 4.1.5 on 2023-01-31 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkings', '0018_alter_price_end_time_alter_price_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='user',
            field=models.TextField(max_length=50),
        ),
    ]
