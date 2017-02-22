from django.db import transaction
from django.shortcuts import redirect, reverse, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib import messages

from braces.views import LoginRequiredMixin, UserFormKwargsMixin

from .models import MyBrick
from .forms import MyBrickForm, ItemFormCreateSet, ItemFormUpdateSet, ItemSoldFormSet
from .viewmixins import BrickSetFormKwargsMixin
from .utils import update_mybrick_record


class MyBrickListView(LoginRequiredMixin, ListView):
    model = MyBrick
    context_object_name = 'mybricks'
    template_name = 'mybricks/list.html'

    def get_queryset(self):
        queryset = super(MyBrickListView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        theme_title = self.kwargs.get('theme_title', None)
        return queryset.filter(brickset__theme_title=theme_title) if theme_title else queryset

    def get_context_data(self, **kwargs):
        context = super(MyBrickListView, self).get_context_data(**kwargs)
        mybricks = context['mybricks']
        buying_price = 0
        estimated_price = 0
        profit = 0
        official_price = 0
        for mybrick in mybricks:
            buying_price += float(mybrick.total_buying_price or 0)
            estimated_price += mybrick.total_estimated
            profit += mybrick.estimated_profit
            official_price += float(mybrick.brickset.official_price * mybrick.quantity)
        context.update({
            'buying_price': buying_price,
            'estimated_price': estimated_price,
            'profit': profit,
            'official_price': official_price,
        })
        return context


class DispatchMyBrickByBrickCodeMixin(object):
    def get_object(self, queryset=None):
        return get_object_or_404(MyBrick, brickset__brick_code=self.kwargs.get('brick_code'))


class MyBrickDetailView(LoginRequiredMixin, DispatchMyBrickByBrickCodeMixin, DetailView):
    model = MyBrick
    context_object_name = 'mybrick'
    template_name = 'mybricks/detail.html'

    def get_queryset(self):
        update_mybrick_record(self.request.user)
        return super(MyBrickDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(MyBrickDetailView, self).get_context_data(**kwargs)
        context['estimation'] = self.object.estimation
        return context


class MyBrickCreateView(LoginRequiredMixin, UserFormKwargsMixin, BrickSetFormKwargsMixin, CreateView):
    form_class = MyBrickForm
    template_name = 'mybricks/mybrick_form.html'

    def get_success_url(self):
        return redirect(reverse('mybricks:detail', args=[self.object.brickset.brick_code]))

    def dispatch(self, request, *args, **kwargs):
        handler = super(MyBrickCreateView, self).dispatch(request, *args, **kwargs)
        existing = MyBrick.objects.filter(brickset=self.brickset).filter(user=request.user)
        if existing.count() > 0:
            return redirect(reverse('mybricks:detail', args=[str(existing[0].brickset.brick_code)]))
        return handler

    def get_no_brickset_url(self):
        return reverse('sets:product_search_for_add')

    def get_context_data(self, **kwargs):
        context = super(MyBrickCreateView, self).get_context_data(**kwargs)
        context['brickset'] = self.brickset

        if self.request.POST:
            context['items'] = ItemFormCreateSet(self.request.POST)
        else:
            formset = ItemFormCreateSet()
            for item_form in formset:
                item_form.initial = {'buying_price': self.brickset.official_price}
            context['items'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_form = context['items']
        with transaction.atomic():
            self.object = form.save()
            if items_form.is_valid():
                items_form.instance = self.object
                items_form.save()
                messages.success(self.request, 'You successfully added a brick.', extra_tags='My Bricks')
        return super(MyBrickCreateView, self).form_valid(form)


class MyBrickUpdateView(LoginRequiredMixin, UserFormKwargsMixin, DispatchMyBrickByBrickCodeMixin, UpdateView):
    model = MyBrick
    form_class = MyBrickForm
    template_name = 'mybricks/mybrick_form.html'
    context_object_name = 'mybrick'

    def get_context_data(self, **kwargs):
        context = super(MyBrickUpdateView, self).get_context_data(**kwargs)
        context['brickset'] = self.object.brickset

        if self.request.POST:
            context['items'] = ItemFormUpdateSet(self.request.POST, instance=self.object, queryset=self.object.item_set.unsold())
        else:
            context['items'] = ItemFormUpdateSet(instance=self.object, queryset=self.object.item_set.unsold())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_form = context['items']
        existing_items = self.object.item_set.unsold()
        with transaction.atomic():
            self.object = form.save()
            if not items_form.is_valid():
                return self.form_invalid(form)
            if len(items_form) == 0:
                self.object.delete()
                return redirect(reverse('mybricks:list'))
            items_form.instance = self.object
            items_form.save()
            items = [i.instance for i in items_form]
            [i.delete() for i in existing_items if not list(filter(lambda item: item.id == i.id, items))]
            messages.info(self.request, 'You brick is just updated', extra_tags='My Bricks')
        return super(MyBrickUpdateView, self).form_valid(form)


class MyBrickSoldView(LoginRequiredMixin, UserFormKwargsMixin, DispatchMyBrickByBrickCodeMixin, UpdateView):
    model = MyBrick
    form_class = MyBrickForm
    template_name = 'mybricks/mybrick_sold_form.html'
    context_object_name = 'mybrick'

    def get_context_data(self, **kwargs):
        context = super(MyBrickSoldView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['items'] = ItemSoldFormSet(self.request.POST, queryset=self.object.item_set.all().order_by('sold'))
        else:
            context['items'] = ItemSoldFormSet(queryset=self.object.item_set.all().order_by('sold'))
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_form = context['items']
        with transaction.atomic():
            if not items_form.is_valid():
                return self.form_invalid(form)
            items_form.save()
            messages.info(self.request, 'You brick is just updated', extra_tags='My Bricks')
        return super(MyBrickSoldView, self).form_valid(form)
