# Generated by Django 4.2.6 on 2024-01-04 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_alter_contact_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='sup_loc',
            field=models.CharField(max_length=50),
        ),
    ]
