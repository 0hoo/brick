class ReadonlyDatesAdminMixin(object):
    readonly_fields = ('created', 'modified', )


class SearchByProductAdminMixin(object):
    search_fields = ['product__product_code', 'product__title']


class ListFilterCreatedAdminMixin(object):
    list_filter = ['created']