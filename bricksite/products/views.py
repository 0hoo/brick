from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from braces.views import LoginRequiredMixin

from .viewmixins import NullOrderableListMixin
from .models import Product
from .forms import ProductForm

from items.models import Item
from bookmarks.models import Bookmark


class ProductListView(LoginRequiredMixin, NullOrderableListMixin, ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/list.html'
    paginate_by = 40
    order_by = 'official_price'
    ordering = 'desc'

    def get_queryset(self):
        queryset = super(ProductListView, self).get_queryset()
        theme_title = self.kwargs.get('theme_title', None)
        return queryset.filter(theme_title=theme_title) if theme_title else queryset

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        theme_title = self.kwargs.get('theme_title', None)
        theme_titles = Product.objects.theme_titles()

        adjacent_pages = 3
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
            'theme_titles': theme_titles,
            'theme_title': theme_title,
        })
        return context


class ProductSearchForAddView(LoginRequiredMixin, NullOrderableListMixin, ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/search.html'
    paginate_by = 50
    order_by = 'official_price'
    ordering = 'desc'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        if search:
            return self.model.objects.search(search)
        else:
            return Product.objects.none()


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'products/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        product = self.get_object()
        context['have_item'] = Item.objects.user_has_item(self.request.user, product)
        existing_bookmarks = Bookmark.objects.filter(product=product).filter(user=self.request.user)
        if existing_bookmarks.count() > 0:
            context['have_bookmark'] = existing_bookmarks[0]

        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
