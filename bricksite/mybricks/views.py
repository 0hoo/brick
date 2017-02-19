from django.db import transaction
from django.shortcuts import redirect, reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, FormView
from django.contrib import messages

from braces.views import LoginRequiredMixin, UserFormKwargsMixin

from .models import MyBrick
from .forms import ItemForm, ThingFormCreateSet, ThingFormUpdateSet, ThingSoldFormSet
from .viewmixins import BrickSetFormKwargsMixin
from .utils import update_item_record


class ItemListView(LoginRequiredMixin, ListView):
    model = MyBrick
    context_object_name = 'items'
    template_name = 'mybricks/list.html'

    def get_queryset(self):
        queryset = super(ItemListView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        theme_title = self.kwargs.get('theme_title', None)
        return queryset.filter(brickset__theme_title=theme_title) if theme_title else queryset

    def get_context_data(self, **kwargs):
        context = super(ItemListView, self).get_context_data(**kwargs)
        items = context['items']
        buying_price = 0
        estimated_price = 0
        profit = 0
        official_price = 0
        for item in items:
            buying_price += float(item.total_buying_price or 0)
            estimated_price += item.total_estimated
            profit += item.estimated_profit
            official_price += float(item.brickset.official_price * item.quantity)
        context.update({
            'buying_price': buying_price,
            'estimated_price': estimated_price,
            'profit': profit,
            'official_price': official_price,
        })
        return context


class ItemDetailView(LoginRequiredMixin, DetailView):
    model = MyBrick
    context_object_name = 'item'
    template_name = 'mybricks/detail.html'

    def get_queryset(self):
        update_item_record(self.request.user)
        return super(ItemDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context['estimation'] = self.object.estimation
        return context


class EditItemView(LoginRequiredMixin, UserFormKwargsMixin, UpdateView):
    form_class = ItemForm
    model = MyBrick
    template_name = 'mybricks/item_form.html'

    def get_context_data(self, **kwargs):
        context = super(EditItemView, self).get_context_data(**kwargs)
        context['brickset'] = self.object.brickset
        return context


class ItemCreateView(LoginRequiredMixin, UserFormKwargsMixin, BrickSetFormKwargsMixin, CreateView):
    form_class = ItemForm
    template_name = 'mybricks/item_form.html'

    def get_success_url(self):
        return redirect(reverse('mybricks:detail', args=[self.object.id]))

    def dispatch(self, request, *args, **kwargs):
        handler = super(ItemCreateView, self).dispatch(request, *args, **kwargs)
        existing_items = MyBrick.objects.filter(brickset=self.brickset).filter(user=request.user)
        if existing_items.count() > 0:
            return redirect(reverse('mybricks:detail', args=[str(existing_items[0].id)]))
        return handler

    def get_no_brickset_url(self):
        return reverse('sets:product_search_for_add')

    def get_context_data(self, **kwargs):
        context = super(ItemCreateView, self).get_context_data(**kwargs)
        context['brickset'] = self.brickset

        if self.request.POST:
            context['things'] = ThingFormCreateSet(self.request.POST)
        else:
            formset = ThingFormCreateSet()
            for thing_form in formset:
                thing_form.initial = {'buying_price': self.brickset.official_price}
            context['things'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        things_form = context['things']
        with transaction.atomic():
            self.object = form.save()
            if things_form.is_valid():
                things_form.instance = self.object
                things_form.save()
                messages.success(self.request, 'You successfully added a brick item.', extra_tags='Items')
        return super(ItemCreateView, self).form_valid(form)


class ItemUpdateView(LoginRequiredMixin, UserFormKwargsMixin, UpdateView):
    model = MyBrick
    form_class = ItemForm
    template_name = 'mybricks/item_form.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super(ItemUpdateView, self).get_context_data(**kwargs)
        context['brickset'] = self.object.brickset

        if self.request.POST:
            context['things'] = ThingFormUpdateSet(self.request.POST, instance=self.object, queryset=self.object.thing_set.unsold())
        else:
            context['things'] = ThingFormUpdateSet(instance=self.object, queryset=self.object.thing_set.unsold())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        things_form = context['things']
        existing_things = self.object.thing_set.unsold()
        with transaction.atomic():
            self.object = form.save()
            if not things_form.is_valid():
                return self.form_invalid(form)
            if len(things_form) == 0:
                self.object.delete()
                return redirect(reverse('mybricks:list'))
            things_form.instance = self.object
            things_form.save()
            things = [t.instance for t in things_form]
            [t.delete() for t in existing_things if not list(filter(lambda thing: thing.id == t.id, things))]
            messages.success(self.request, 'You brick item is just updated', extra_tags='Items')
        return super(ItemUpdateView, self).form_valid(form)


class ItemSoldView(LoginRequiredMixin, UserFormKwargsMixin, UpdateView):
    model = MyBrick
    form_class = ItemForm
    template_name = 'mybricks/item_sold_form.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super(ItemSoldView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['things'] = ThingSoldFormSet(self.request.POST, queryset=self.object.thing_set.all().order_by('sold'))
        else:
            context['things'] = ThingSoldFormSet(queryset=self.object.thing_set.all().order_by('sold'))
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        things_form = context['things']
        with transaction.atomic():
            if not things_form.is_valid():
                return self.form_invalid(form)
            things_form.save()
            messages.success(self.request, 'You brick item is just updated', extra_tags='Items')
        return super(ItemSoldView, self).form_valid(form)
