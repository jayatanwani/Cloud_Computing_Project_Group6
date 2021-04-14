from django.db import models
from django.contrib.auth.models import User

class UserBuckets(models.Model):
    Bucket_name = models.CharField(max_length=200)
    Bucket_Creation_time_stamp = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class UserFiles(models.Model):
    File_name = models.CharField(max_length=150)
    File_Creation_time_stamp = models.DateTimeField(null=True, blank=True)
    File_description = models.TextField(blank=True)
    File_url = models.URLField(default=None)
    File_size = models.CharField(max_length=150)
    bucket_id = models.IntegerField()
