# Generated by Django 5.0.1 on 2024-09-30 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_customer_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='status',
            field=models.IntegerField(choices=[(0, 'Suspended'), (1, 'Active')], default=0),
        ),
    ]