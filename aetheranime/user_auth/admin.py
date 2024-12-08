from django.contrib import admin
from .models import CustomUser, History, Status, Review, Comment

admin.site.register(CustomUser)
admin.site.register(History)
admin.site.register(Status)
admin.site.register(Review)
admin.site.register(Comment)
