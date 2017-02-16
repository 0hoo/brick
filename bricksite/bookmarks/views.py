from django.views.generic import ListView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe

from braces.views import LoginRequiredMixin

from .models import Bookmark

from products.models import Product

class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    context_object_name = 'bookmarks'
    template_name = 'bookmarks/list.html'


class BookmarkUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        product_id = request.GET.get('product_id', None)
        product = get_object_or_404(Product, pk=product_id)
        Bookmark.objects.get_or_create(
            product=product,
            user=request.user
        )
        link_text = '<a href="' + reverse('bookmarks:list') + '">Check my bookmarks</a>.'
        messages.info(request, mark_safe('This set is bookmarked. ' + link_text), extra_tags='Bookmarks')
        return redirect(product)