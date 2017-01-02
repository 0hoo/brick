from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

app_name = 'users'

urlpatterns = [
    url(r'^api/$', views.UserViewSet.as_view({'get': 'retrieve'})),
    url(r'^register/$', views.SiteRegistrationView.as_view(), name='register'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, {'next_page': '/users/login'}, name='logout'),
]