from django.db.models import Count

from braces.views import OrderableListMixin

class BrickOrderableListMixin(OrderableListMixin):
    def get_ordered_queryset(self, queryset=None):
        order_by = self.order_by
        self.ordering = self.request.GET.get("ordering", (self.ordering or "asc"))

        if order_by and self.ordering == "desc":
            sorted_order_by = "-" + order_by
        return queryset.annotate(null_order_by=Count(order_by)).order_by('-null_order_by', sorted_order_by)
