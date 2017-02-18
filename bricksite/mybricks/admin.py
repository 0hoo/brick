from django.contrib import admin

from common.admin import ListFilterCreatedAdminMixin, ReadonlyDatesAdminMixin, SearchByProductAdminMixin
from .models import Item, ItemRecord, Thing


class ItemAdmin(ListFilterCreatedAdminMixin, SearchByProductAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    search_fields = SearchByProductAdminMixin.search_fields + ['user__username']


class ItemRecordAdmin(ListFilterCreatedAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    pass


class ThingAdmin(ReadonlyDatesAdminMixin, admin.ModelAdmin):
    pass


admin.site.register(Item, ItemAdmin)
admin.site.register(ItemRecord, ItemRecordAdmin)
admin.site.register(Thing, ThingAdmin)
