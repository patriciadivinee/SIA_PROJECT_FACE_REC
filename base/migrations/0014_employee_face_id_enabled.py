# Generated by Django 4.2.6 on 2024-01-17 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='face_id_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
