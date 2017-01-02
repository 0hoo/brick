from django.conf.urls import url

from . import views

app_name = 'products'

urlpatterns = [
    url(r'^$', views.ProductListView.as_view(), name='list'),
    url(r'^(?P<pk>[0-9]+)/$', views.ProductDetailView.as_view(), name='detail'),
]
