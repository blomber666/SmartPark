# Generated by Django 4.1.5 on 2023-01-30 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkings', '0014_alter_price_end_time_alter_price_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='end_time',
            field=models.TimeField(blank=True, default='23:59:59'),
        ),
        migrations.AlterField(
            model_name='price',
            name='start_time',
            field=models.TimeField(blank=True, default='00:00:00'),
        ),
    ]
