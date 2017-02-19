from django.conf.urls import url

from . import views

app_name = 'mybricks'

urlpatterns = [
    url(r'^$', views.MyBrickListView.as_view(), name='list'),
    url(r'^list/(?P<theme_title>[^/]+)/$', views.MyBrickListView.as_view(), name='list_by_theme'),
    url(r'^add/$', views.MyBrickCreateView.as_view(), name='add'),
    url(r'^(?P<pk>[0-9]+)/$', views.MyBrickDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.MyBrickUpdateView.as_view(), name='edit'),
    url(r'^(?P<pk>[0-9]+)/sold/$', views.MyBrickSoldView.as_view(), name='sold'),
]
