# Generated by Django 4.2.7 on 2024-01-12 00:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_membership_type_alter_post_post_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='desscription',
            new_name='description',
        ),
    ]
