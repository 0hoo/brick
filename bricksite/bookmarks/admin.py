from django.contrib import admin

from .models import Bookmark


class BookmarkAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'brickset__product_code']

admin.site.register(Bookmark, BookmarkAdmin)
