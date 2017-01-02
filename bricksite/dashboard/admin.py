from django.contrib import admin

from .models import Dashboard


class DashboardAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'target_at']
    list_filter = ['target_at']

admin.site.register(Dashboard, DashboardAdmin)
