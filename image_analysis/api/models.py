from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

IMAGE_DIR = "media/images/"
FILE_DIR = "media/meta/"


class Image(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    url = models.CharField(max_length=500)
    labels = models.CharField(max_length=9000)
    name = models.CharField(max_length=500)


class MetaFile(models.Model):
    id = models.CharField(primary_key=True, max_length=600)
