from django.conf.urls import url

from . import views

app_name = 'items'

urlpatterns = [
    url(r'^$', views.ItemListView.as_view(), name='list'),
    url(r'^add/$', views.ItemCreateView.as_view(), name='add'),
    url(r'^(?P<pk>[0-9]+)/$', views.ItemDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.ItemUpdateView.as_view(), name='edit'),
]
