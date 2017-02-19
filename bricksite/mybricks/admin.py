from django.contrib import admin

from common.admin import ListFilterCreatedAdminMixin, ReadonlyDatesAdminMixin, SearchByBrickSetAdminMixin
from .models import MyBrick, MyBrickRecord, MyBrickItem


class MyBrickAdmin(ListFilterCreatedAdminMixin, SearchByBrickSetAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    search_fields = SearchByBrickSetAdminMixin.search_fields + ['user__username']


class MyBrickRecordAdmin(ListFilterCreatedAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    pass


class MyBrickItemAdmin(ReadonlyDatesAdminMixin, admin.ModelAdmin):
    pass


admin.site.register(MyBrick, MyBrickAdmin)
admin.site.register(MyBrickRecord, MyBrickRecordAdmin)
admin.site.register(MyBrickItem, MyBrickItemAdmin)
