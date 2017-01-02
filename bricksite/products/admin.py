from django.contrib import admin

from common.admin import ListFilterCreatedAdminMixin, ReadonlyDatesAdminMixin, SearchByProductAdminMixin
from .models import Product, BricklinkRecord, EbayRecord, EbayItem


class ProductAdmin(ListFilterCreatedAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    search_fields = ['product_code', 'title']


class BricklinkRecordAdmin(ListFilterCreatedAdminMixin, SearchByProductAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    pass


class EbayRecordAdmin(ListFilterCreatedAdminMixin, SearchByProductAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    pass


class EbayItemAdmin(SearchByProductAdminMixin, ReadonlyDatesAdminMixin, admin.ModelAdmin):
    list_filter = ['used']


admin.site.register(Product, ProductAdmin)
admin.site.register(BricklinkRecord, BricklinkRecordAdmin)
admin.site.register(EbayRecord, EbayRecordAdmin)
admin.site.register(EbayItem, EbayItemAdmin)
