# Generated by Django 4.1.5 on 2023-01-31 02:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parkings', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stop',
            old_name='user',
            new_name='user_id',
        ),
    ]
