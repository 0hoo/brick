from django.shortcuts import redirect, reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.db import transaction

from braces.views import LoginRequiredMixin, UserFormKwargsMixin

from .models import Item
from .forms import ItemForm, ThingFormCreateSet, ThingFormUpdateSet
from .viewmixins import ProductFormKwargsMixin
from .utils import update_item_record

from products.models import Product


class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    context_object_name = 'items'
    template_name = 'items/list.html'

    def get_queryset(self):
        queryset = super(ItemListView, self).get_queryset()
        return queryset.filter(user=self.request.user)


class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    context_object_name = 'item'
    template_name = 'items/detail.html'

    def get_queryset(self):
        update_item_record(self.request.user)
        return super(ItemDetailView, self).get_queryset()


class EditItemView(LoginRequiredMixin, UserFormKwargsMixin, UpdateView):
    form_class = ItemForm
    model = Item
    template_name = 'items/item_form.html'

    def get_context_data(self, **kwargs):
        context = super(EditItemView, self).get_context_data(**kwargs)
        context['product'] = self.object.product
        return context


class AddItemView(LoginRequiredMixin, UserFormKwargsMixin, ProductFormKwargsMixin, CreateView):
    form_class = ItemForm
    template_name = 'items/item_form.html'

    def dispatch(self, request, *args, **kwargs):
        handler = super(UserFormKwargsMixin, self).dispatch(request, *args, **kwargs)
        existing_items = Item.objects.filter(product=self.product).filter(user=request.user)
        if existing_items.count() > 0:
            return redirect(reverse('items:detail', args=[str(existing_items[0].id)]))
        return handler

    def get_no_product_url(self):
        return reverse('products:product_search_for_add')

    def get_context_data(self, **kwargs):
        context = super(AddItemView, self).get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def get_initial(self):
        initial = super(AddItemView, self).get_initial()
        if self.product.official_price:
            initial['buying_price'] = self.product.official_price
        initial['owned'] = True
        return initial


class ItemCreateView(LoginRequiredMixin, UserFormKwargsMixin, ProductFormKwargsMixin, CreateView):
    form_class = ItemForm
    template_name = 'items/item_form.html'

    def get_success_url(self):
        return redirect(reverse('items:detail', args=[self.object.id]))

    def dispatch(self, request, *args, **kwargs):
        handler = super(ItemCreateView, self).dispatch(request, *args, **kwargs)
        existing_items = Item.objects.filter(product=self.product).filter(user=request.user)
        if existing_items.count() > 0:
            return redirect(reverse('items:detail', args=[str(existing_items[0].id)]))
        return handler

    def get_no_product_url(self):
        return reverse('products:product_search_for_add')

    def get_context_data(self, **kwargs):
        context = super(ItemCreateView, self).get_context_data(**kwargs)
        context['product'] = self.product

        if self.request.POST:
            context['things'] = ThingFormCreateSet(self.request.POST)
        else:
            context['things'] = ThingFormCreateSet()
        return context

    def get_initial(self):
        initial = super(ItemCreateView, self).get_initial()
        if self.product.official_price:
            initial['buying_price'] = self.product.official_price
        initial['owned'] = True
        return initial

    def form_valid(self, form):
        context = self.get_context_data()
        things = context['things']
        with transaction.atomic():
            self.object = form.save()
            if things.is_valid():
                things.instance = self.object
                things.save()
        return super(ItemCreateView, self).form_valid(form)


class ItemUpdateView(LoginRequiredMixin, UserFormKwargsMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'items/item_form.html'

    def get_context_data(self, **kwargs):
        context = super(ItemUpdateView, self).get_context_data(**kwargs)
        context['product'] = self.object.product

        if self.request.POST:
            context['things'] = ThingFormUpdateSet(self.request.POST, instance=self.object)
        else:
            context['things'] = ThingFormUpdateSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        things = context['things']
        with transaction.atomic():
            self.object = form.save()
            if things.is_valid():
                things.instance = self.object
                things.save()
        return super(ItemUpdateView, self).form_valid(form)
