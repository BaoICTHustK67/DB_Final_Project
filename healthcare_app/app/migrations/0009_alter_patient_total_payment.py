# Generated by Django 4.2.7 on 2024-01-12 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_patient_total_order_patient_total_payment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='total_payment',
            field=models.IntegerField(default=0, null=True),
        ),
    ]