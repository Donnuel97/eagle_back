# Generated by Django 5.0.1 on 2024-09-30 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alter_customer_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='activation_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
