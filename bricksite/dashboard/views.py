from django.views.generic import ListView
from braces.views import LoginRequiredMixin

from .utils import snapshot_latest_dashboard

from .models import item_count_by_theme, item_quantity_by_theme, official_price_by_theme, total_prices_by_theme
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

        total_estimated_by_theme, total_profit_by_theme, total_buying_price_by_theme = total_prices_by_theme(self.request.user)

        context.update({
            'dashboard': dashboard,
            'show_profit_chart': self.show_profit_chart,
            'item_count_by_theme': item_count_by_theme(self.request.user),
            'item_quantity_by_theme': item_quantity_by_theme(self.request.user),
            'official_price_by_theme': official_price_by_theme(self.request.user),
            'total_estimated_by_theme': total_estimated_by_theme,
            'total_profit_by_theme': total_profit_by_theme,
            'total_buying_price_by_theme': total_buying_price_by_theme,
        })
        return context
