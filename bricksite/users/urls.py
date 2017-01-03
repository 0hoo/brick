from django.conf.urls import url
from django.contrib.auth.views import login, logout

app_name = 'users'

urlpatterns = [
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, {'next_page': '/users/login'}, name='logout'),
]
