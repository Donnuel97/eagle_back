# Generated by Django 5.0.1 on 2024-02-05 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alter_payments_payment_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payments',
            name='payment_duration',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
