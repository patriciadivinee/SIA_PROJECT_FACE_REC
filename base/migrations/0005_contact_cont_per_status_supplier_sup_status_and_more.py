# Generated by Django 4.2.6 on 2024-01-02 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_contact_cont_per_fb_acc_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='cont_per_status',
            field=models.CharField(default='Active', max_length=10),
        ),
        migrations.AddField(
            model_name='supplier',
            name='sup_status',
            field=models.CharField(default='Active', max_length=10),
        ),
        migrations.AlterField(
            model_name='contact',
            name='sup_id',
            field=models.ForeignKey(db_column='sup_id', on_delete=django.db.models.deletion.CASCADE, to='base.supplier'),
        ),
    ]
