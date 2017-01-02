from django.conf.urls import url

from . import views

app_name = 'dashboard'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
]
