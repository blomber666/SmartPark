# Generated by Django 4.1.5 on 2023-01-29 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkings', '0010_rename_complete_stops_statistic_completed_stops'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistic',
            name='average_time',
            field=models.DurationField(),
        ),
    ]
