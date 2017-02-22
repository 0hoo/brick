from django.views.generic import ListView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe

from braces.views import LoginRequiredMixin

from .models import Bookmark

from sets.models import BrickSet


class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    context_object_name = 'bookmarks'
    template_name = 'bookmarks/list.html'

    def get_queryset(self):
        queryset = super(BookmarkListView, self).get_queryset()
        return queryset.filter(user=self.request.user).order_by('-id')


class BookmarkUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        brick_code = request.GET.get('brick_code', None)
        brickset = get_object_or_404(BrickSet, brick_code=brick_code)
        Bookmark.objects.get_or_create(
            brickset=brickset,
            user=request.user
        )
        link_text = '<a href="' + reverse('bookmarks:list') + '">Check my bookmarks</a>.'
        messages.info(request, mark_safe('This set is bookmarked. ' + link_text), extra_tags='Bookmarks')
        return redirect(brickset)
