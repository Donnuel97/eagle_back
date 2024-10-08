# Generated by Django 5.0.1 on 2024-10-01 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_agent_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo_header_color', models.CharField(default='dark', max_length=20)),
                ('navbar_color', models.CharField(default='white', max_length=20)),
                ('sidebar_color', models.CharField(default='dark', max_length=20)),
            ],
        ),
    ]
