from django.conf.urls import url

from . import views

app_name = 'sets'

urlpatterns = [
    url(r'^$', views.BrickSetListView.as_view(), name='list'),
    url(r'^theme/(?P<theme_title>[^/]+)/$', views.BrickSetListView.as_view(), name='list_by_theme'),
    url(r'^search/add/$', views.BrickSetSearchForAddView.as_view(), name='search'),
    url(r'^(?P<brick_code>[0-9]+)/$', views.BrickSetDetailView.as_view(), name='detail'),
    url(r'^add/$', views.BrickSetCreateView.as_view(), name='add'),
]
