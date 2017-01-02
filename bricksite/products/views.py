from django.views.generic import ListView, DetailView

from braces.views import LoginRequiredMixin

from .models import Product

from items.models import Item


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        adjacent_pages = 9
        page_number = context['page_obj'].number
        num_pages = context['paginator'].num_pages
        start_page = max(page_number - adjacent_pages, 1)
        if start_page <= 3:
            start_page = 1
        edit_page = page_number + adjacent_pages + 1
        if edit_page >= num_pages - 1:
            edit_page = num_pages + 1
        page_numbers = [n for n in range(start_page, edit_page) if n > 0 and n <= num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': num_pages not in page_numbers,
        })
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'products/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        existing_items = Item.objects.filter(product=self.get_object()).filter(user=self.request.user)
        if existing_items.count() > 0:
            context['have_item'] = existing_items[0]

        return context
