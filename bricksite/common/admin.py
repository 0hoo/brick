class ReadonlyDatesAdminMixin(object):
    readonly_fields = ('created', 'modified', )


class SearchByProductAdminMixin(object):
    search_fields = ['brickset__product_code', 'brickset__title']


class ListFilterCreatedAdminMixin(object):
    list_filter = ['created']