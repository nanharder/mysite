from django.contrib import admin
from .models import LikeCount,LikeRecord

@admin.register(LikeCount)
class LikeCountAdmin(admin.ModelAdmin):
    list_display = ('id',)

@admin.register(LikeRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ('id',)
