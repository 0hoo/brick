from django.conf.urls import url

from . import views

app_name = 'products'

urlpatterns = [
    url(r'^$', views.ProductListView.as_view(), name='list'),
    url(r'^theme/(?P<theme_title>[^/]+)/$', views.ProductListView.as_view(), name='list_by_theme'),
    url(r'^search/add/$', views.ProductSearchForAddView.as_view(), name='search'),
    url(r'^(?P<pk>[0-9]+)/$', views.ProductDetailView.as_view(), name='detail'),
    url(r'^add/$', views.ProductCreateView.as_view(), name='add'),
]
