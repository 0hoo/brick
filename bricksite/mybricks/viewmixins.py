from django.http import Http404
from django.shortcuts import redirect

from sets.models import BrickSet


class ProductDispatchMixin(object):
    product = None

    def get_no_product_url(self):
        return ''

    def dispatch(self, request, *args, **kwargs):
        brick_code = request.GET.get('product', '')
        if not brick_code:
            return redirect(self.get_no_product_url())
        try:
            self.product = BrickSet.objects.get(brick_code=brick_code)
        except BrickSet.DoesNotExist:
            raise Http404('Product does not exist')
        return super(ProductDispatchMixin, self).dispatch(request, *args, **kwargs)


class ProductFormKwargsMixin(ProductDispatchMixin):

    def get_form_kwargs(self):
        kwargs = super(ProductFormKwargsMixin, self).get_form_kwargs()
        kwargs.update({"product": self.product})
        return kwargs