from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView

from braces.views import LoginRequiredMixin

from .viewmixins import NullOrderableListMixin
from .models import BrickSet
from .forms import BrickSetForm

from mybricks.models import MyBrick
from bookmarks.models import Bookmark


class BrickSetListView(LoginRequiredMixin, NullOrderableListMixin, ListView):
    model = BrickSet
    context_object_name = 'bricksets'
    template_name = 'sets/list.html'
    paginate_by = 40
    order_by = 'official_price'
    ordering = 'desc'

    def get_queryset(self):
        queryset = super(BrickSetListView, self).get_queryset()
        theme_title = self.kwargs.get('theme_title', None)
        return queryset.filter(theme_title=theme_title) if theme_title else queryset

    def get_context_data(self, **kwargs):
        context = super(BrickSetListView, self).get_context_data(**kwargs)
        theme_title = self.kwargs.get('theme_title', None)
        theme_titles = BrickSet.objects.theme_titles()

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


class BrickSetSearchForAddView(LoginRequiredMixin, NullOrderableListMixin, ListView):
    model = BrickSet
    context_object_name = 'bricksets'
    template_name = 'sets/search.html'
    paginate_by = 50
    order_by = 'official_price'
    ordering = 'desc'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        if search:
            return self.model.objects.search(search)
        else:
            return BrickSet.objects.none()


class BrickSetDetailView(LoginRequiredMixin, DetailView):
    model = BrickSet
    context_object_name = 'brickset'
    template_name = 'sets/detail.html'

    def get_context_data(self, **kwargs):
        context = super(BrickSetDetailView, self).get_context_data(**kwargs)
        brickset = self.get_object()
        context['have_mybrick'] = MyBrick.objects.user_brickset(self.request.user, brickset)
        existing_bookmarks = Bookmark.objects.filter(brickset=brickset).filter(user=self.request.user)
        if existing_bookmarks.count() > 0:
            context['have_bookmark'] = existing_bookmarks[0]

        return context


class BrickSetCreateView(LoginRequiredMixin, CreateView):
    model = BrickSet
    form_class = BrickSetForm
    template_name = 'sets/form.html'
