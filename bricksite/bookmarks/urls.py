from django.conf.urls import url

from . import views

app_name = 'bookmarks'

urlpatterns = [
    url(r'^$', views.BookmarkListView.as_view(), name='list'),
    url(r'^edit/$', views.BookmarkUpdateView.as_view(), name='update'),
]
