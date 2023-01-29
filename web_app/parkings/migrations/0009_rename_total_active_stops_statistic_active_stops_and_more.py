# Generated by Django 4.1.5 on 2023-01-28 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkings', '0008_alter_stop_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statistic',
            old_name='total_active_stops',
            new_name='active_stops',
        ),
        migrations.AddField(
            model_name='statistic',
            name='average_income_per_hour',
            field=models.DecimalField(decimal_places=2, max_digits=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statistic',
            name='average_price',
            field=models.DecimalField(decimal_places=2,  max_digits=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statistic',
            name='average_stops_per_hour',
            field=models.DecimalField(decimal_places=2,  max_digits=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statistic',
            name='average_time',
            field=models.TimeField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statistic',
            name='complete_stops',
            field=models.IntegerField(),
            preserve_default=False,
        ),
    ]