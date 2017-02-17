from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/settings.html'
