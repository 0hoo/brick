from django.contrib.auth.models import User

from registration.backends.simple.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail

from rest_framework import viewsets
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class SiteRegistrationView(RegistrationView):
    form_class = RegistrationFormUniqueEmail

    def get_success_url(self, user):
        return '/products'
