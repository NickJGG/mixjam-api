from django.db import models

class Artist(models.Model):
    spotify_id = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    image_url = models.URLField()
