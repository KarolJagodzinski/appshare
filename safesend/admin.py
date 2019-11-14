import os
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import File, URL


@admin.register(File)
class AdminFile(admin.ModelAdmin):
    list_display = ("filename", "created_at", "visit_counter", "uuid")

    def filename(self, obj):
        return os.path.basename(obj.file.path)


@admin.register(URL)
class AdminFile(admin.ModelAdmin):
    list_display = ("url", "created_at", "visit_counter", "uuid")
