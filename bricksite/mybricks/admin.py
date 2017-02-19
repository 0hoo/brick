from django.contrib import admin

from common.admin import ListFilterCreatedAdminMixin, ReadonlyDatesAdminMixin, SearchByBrickSetAdminMixin
from .models import MyBrick, MyBrickRecord, MyBrickItem


class ItemAdmin(ListFilterCreatedAdminMixin, SearchByBrickSetAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    search_fields = SearchByBrickSetAdminMixin.search_fields + ['user__username']


class ItemRecordAdmin(ListFilterCreatedAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    pass


class ThingAdmin(ReadonlyDatesAdminMixin, admin.ModelAdmin):
    pass


admin.site.register(MyBrick, ItemAdmin)
admin.site.register(MyBrickRecord, ItemRecordAdmin)
admin.site.register(MyBrickItem, ThingAdmin)
