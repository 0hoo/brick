from django.http import Http404
from django.shortcuts import redirect

from sets.models import BrickSet


class BrickSetDispatchMixin(object):
    product = None

    def get_no_brickset_url(self):
        return ''

    def dispatch(self, request, *args, **kwargs):
        brick_code = request.GET.get('brickset', '')
        if not brick_code:
            return redirect(self.get_no_brickset_url())
        try:
            self.brickset = BrickSet.objects.get(brick_code=brick_code)
        except BrickSet.DoesNotExist:
            raise Http404('Product does not exist')
        return super(BrickSetDispatchMixin, self).dispatch(request, *args, **kwargs)


class BrickSetFormKwargsMixin(BrickSetDispatchMixin):

    def get_form_kwargs(self):
        kwargs = super(BrickSetFormKwargsMixin, self).get_form_kwargs()
        kwargs.update({"brickset": self.brickset})
        return kwargs
