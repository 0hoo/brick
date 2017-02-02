from django.views.generic import ListView
from braces.views import LoginRequiredMixin

from .utils import snapshot_latest_dashboard

from products.models import Product


class IndexView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/index.html'
    model = Product
    context_object_name = 'products'
    show_profit_chart = False

    def get_queryset(self):
        self.show_profit_chart = self.request.GET.get('chart', '') == 'profit'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        dashboard = snapshot_latest_dashboard(self.request.user)
        context.update({
            'dashboard': dashboard,
            'show_profit_chart': self.show_profit_chart,
            'official_prices_by_theme': self.request.user.profile.official_prices_by_theme,
            'item_count_by_theme': self.request.user.profile.item_count_by_theme,
            'total_quantity_by_theme': self.request.user.profile.total_quantity_by_theme,
        })
        return context
