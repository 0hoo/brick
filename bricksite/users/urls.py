from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

app_name = 'users'

urlpatterns = [
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, {'next_page': '/users/login'}, name='logout'),
    url(r'^settings/$', views.SettingsView.as_view(), name='settings'),
]
