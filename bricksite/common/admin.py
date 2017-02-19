class ReadonlyDatesAdminMixin(object):
    readonly_fields = ('created', 'modified', )


class SearchByBrickSetAdminMixin(object):
    search_fields = ['brickset__brick_code', 'brickset__title']


class ListFilterCreatedAdminMixin(object):
    list_filter = ['created']