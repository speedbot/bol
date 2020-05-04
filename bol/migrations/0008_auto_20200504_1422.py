# Generated by Django 2.2 on 2020-05-04 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bol', '0007_shipment_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='client',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client', to='bol.Client'),
        ),
    ]