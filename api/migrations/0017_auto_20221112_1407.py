# Generated by Django 3.1.4 on 2022-11-12 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20221112_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='access_token',
            field=models.CharField(blank=True, max_length=210, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='refresh_token',
            field=models.CharField(blank=True, max_length=210, null=True),
        ),
    ]
