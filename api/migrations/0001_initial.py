# Generated by Django 2.2 on 2023-08-18 03:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spotify_id', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=128)),
                ('image_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_sent', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Party',
            fields=[
                ('code', models.CharField(default='default', max_length=30, primary_key=True, serialize=False)),
                ('mode', models.CharField(choices=[('public', 'Public'), ('friendsonly', 'Friends Only'), ('private', 'Private'), ('closed', 'Closed')], default='private', max_length=50)),
                ('invite_code', models.CharField(blank=True, max_length=6, null=True)),
                ('invite_time', models.DateTimeField(blank=True, null=True)),
                ('context_uri', models.CharField(blank=True, max_length=255, null=True)),
                ('track_uri', models.CharField(blank=True, max_length=255, null=True)),
                ('track_index', models.IntegerField(blank=True, default=0)),
                ('track_progress_ms', models.IntegerField(blank=True, default=0, null=True)),
                ('playback_last_action', models.DateTimeField(blank=True, null=True)),
                ('track_last_end', models.DateTimeField(blank=True, null=True)),
                ('playing', models.BooleanField(blank=True, default=False)),
                ('ending', models.BooleanField(blank=True, default=False)),
                ('time_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('allowed_users', models.ManyToManyField(blank=True, related_name='party_allowed_users', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, related_name='party_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PartyMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('code', models.CharField(default='default', max_length=30, primary_key=True, serialize=False)),
                ('title', models.CharField(default='New Room', max_length=150)),
                ('description', models.CharField(default='', max_length=1000)),
                ('banner_color', models.CharField(blank=True, default='ec4a4e', max_length=6, null=True)),
                ('mode', models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('closed', 'Closed')], default='private', max_length=50)),
                ('invite_code', models.CharField(blank=True, max_length=6, null=True)),
                ('invite_time', models.DateTimeField(blank=True, null=True)),
                ('time_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('playlist_id', models.CharField(max_length=50, null=True)),
                ('playlist_image_url', models.CharField(blank=True, max_length=250, null=True)),
                ('active_users', models.ManyToManyField(blank=True, related_name='active_users', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('inactive_users', models.ManyToManyField(blank=True, related_name='inactive_users', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, related_name='users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spotify_username', models.CharField(blank=True, max_length=50, null=True)),
                ('tag_line', models.CharField(default='Jammer', max_length=50)),
                ('access_token', models.CharField(blank=True, max_length=210, null=True)),
                ('refresh_token', models.CharField(blank=True, max_length=210, null=True)),
                ('authorized', models.BooleanField(default=False)),
                ('color', models.CharField(default='1c71ca', max_length=6)),
                ('picture', models.CharField(blank=True, max_length=100, null=True)),
                ('new_user', models.BooleanField(default=True)),
                ('online_count', models.IntegerField(blank=True, default=0)),
                ('friends', models.ManyToManyField(blank=True, related_name='friends', to=settings.AUTH_USER_MODEL)),
                ('party', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_party', to='api.Party')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song_index', models.IntegerField(blank=True, default=0)),
                ('progress_ms', models.IntegerField(blank=True, default=0, null=True)),
                ('last_action', models.DateTimeField(blank=True, null=True)),
                ('last_song_end', models.DateTimeField(blank=True, null=True)),
                ('playing', models.BooleanField(blank=True, default=False)),
                ('room', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.Room')),
            ],
        ),
        migrations.CreateModel(
            name='PartyInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Notification')),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Party')),
            ],
        ),
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Notification')),
            ],
        ),
    ]