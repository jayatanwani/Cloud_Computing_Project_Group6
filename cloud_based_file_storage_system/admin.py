from django.contrib import admin

from .models import UserBuckets,UserFiles

admin.site.register(UserBuckets)

admin.site.register(UserFiles)
