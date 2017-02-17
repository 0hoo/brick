from django.urls import reverse_lazy
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from config import settings

urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('products:list'))),
    url(r'^sets/', include('products.urls')),
    url(r'^bricks/', include('items.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^bookmarks/', include('bookmarks.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.simple.urls')),
]
