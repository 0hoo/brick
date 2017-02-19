from django.contrib import admin

from common.admin import ListFilterCreatedAdminMixin, ReadonlyDatesAdminMixin, SearchByBrickSetAdminMixin
from .models import BrickSet, BricklinkRecord, EbayRecord, EbayItem


class BrickSetAdmin(ListFilterCreatedAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    search_fields = ['product_code', 'title']


class BricklinkRecordAdmin(ListFilterCreatedAdminMixin, SearchByBrickSetAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    pass


class EbayRecordAdmin(ListFilterCreatedAdminMixin, SearchByBrickSetAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    pass


class EbayItemAdmin(SearchByBrickSetAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    list_filter = ['used']


admin.site.register(BrickSet, BrickSetAdmin)
admin.site.register(BricklinkRecord, BricklinkRecordAdmin)
admin.site.register(EbayRecord, EbayRecordAdmin)
admin.site.register(EbayItem, EbayItemAdmin)
