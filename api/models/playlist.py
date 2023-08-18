from channels.db import DatabaseSyncToAsync
from django.db import models
from django.utils import timezone

from api import util

class Playlist(models.Model):
    room = models.OneToOneField("Room", on_delete = models.CASCADE)
    song_index = models.IntegerField(default = 0, blank = True)
    progress_ms = models.IntegerField(default = 0, null = True, blank = True)
    last_action = models.DateTimeField(null = True, blank = True)
    last_song_end = models.DateTimeField(null = True, blank = True)
    playing = models.BooleanField(default = False, blank = True)

    def get_progress(self, user):
        if self.playing:
            progress_ms = util.get_adjusted_progress(self.room)
        else:
            progress_ms = self.progress_ms

        return progress_ms

    def song_end(self):
        now = timezone.now()

        if self.last_song_end is None or (now - self.last_song_end).total_seconds() > 5:
            self.last_song_end = now
            self.save()

            self.next_song()

            return True
        
        return False

    def previous_song(self):
        self.song_index = self.song_index - 1 if self.song_index > 0 else 0
        self.progress_ms = 0
        self.save()
    
    def next_song(self):
        self.song_index += 1
        self.progress_ms = 0
        self.save()

    @DatabaseSyncToAsync
    def restart(self):
        self.song_index = 0
        self.progress_ms = 0
        self.save()
