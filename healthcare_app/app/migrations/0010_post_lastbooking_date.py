# Generated by Django 4.2.7 on 2024-01-12 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_patient_total_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='lastbooking_date',
            field=models.DateField(null=True),
        ),
    ]
