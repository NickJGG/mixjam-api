# Generated by Django 2.2 on 2023-08-22 00:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0003_auto_20230821_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='track_ender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='track_ender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='party',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL),
        ),
    ]