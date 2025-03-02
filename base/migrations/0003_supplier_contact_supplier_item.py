# Generated by Django 4.2.6 on 2024-01-02 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_requisition_requisitionitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('sup_id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('sup_company', models.CharField(max_length=30, unique=True)),
                ('sup_fname', models.CharField(max_length=30)),
                ('sup_mname', models.CharField(blank=True, max_length=30)),
                ('sup_lname', models.CharField(max_length=30)),
                ('sup_loc', models.CharField(max_length=30)),
                ('sup_mobile', models.CharField(max_length=11, unique=True)),
                ('sup_email', models.CharField(max_length=30, unique=True)),
                ('sup_fb_acc', models.CharField(max_length=150)),
            ],
            options={
                'db_table': 'supplier',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('cont_per_id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('cont_per_fname', models.CharField(max_length=30)),
                ('cont_per_mname', models.CharField(blank=True, max_length=30)),
                ('cont_per_lname', models.CharField(max_length=30)),
                ('cont_per_mobile', models.CharField(max_length=11, unique=True)),
                ('cont_per_email', models.CharField(max_length=30, unique=True)),
                ('cont_per_fb_acc', models.CharField(max_length=150, unique=True)),
                ('sup_id', models.OneToOneField(db_column='sup_id', on_delete=django.db.models.deletion.CASCADE, to='base.supplier')),
            ],
            options={
                'db_table': 'contact_person',
            },
        ),
        migrations.CreateModel(
            name='Supplier_Item',
            fields=[
                ('supit_id', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('prod_id', models.ForeignKey(db_column='prod_id', on_delete=django.db.models.deletion.CASCADE, to='base.product')),
                ('sup_id', models.ForeignKey(db_column='sup_id', on_delete=django.db.models.deletion.CASCADE, to='base.supplier')),
            ],
            options={
                'db_table': 'supplier_item',
                'unique_together': {('sup_id', 'prod_id')},
            },
        ),
    ]
