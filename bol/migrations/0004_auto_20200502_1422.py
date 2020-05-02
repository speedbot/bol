# Generated by Django 2.2 on 2020-05-02 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bol', '0003_client_auth_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='client_id',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='shipmentId',
            field=models.IntegerField(db_index=True, unique=True),
        ),
        migrations.AlterField(
            model_name='transport',
            name='transportId',
            field=models.IntegerField(db_index=True, unique=True),
        ),
    ]
