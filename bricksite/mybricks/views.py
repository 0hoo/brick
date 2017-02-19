from django.db import transaction
from django.shortcuts import redirect, reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib import messages

from braces.views import LoginRequiredMixin, UserFormKwargsMixin

from .models import MyBrick
from .forms import MyBrickForm, ThingFormCreateSet, ThingFormUpdateSet, ThingSoldFormSet
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


class MyBrickDetailView(LoginRequiredMixin, DetailView):
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
        return redirect(reverse('mybricks:detail', args=[self.object.id]))

    def dispatch(self, request, *args, **kwargs):
        handler = super(MyBrickCreateView, self).dispatch(request, *args, **kwargs)
        existing = MyBrick.objects.filter(brickset=self.brickset).filter(user=request.user)
        if existing.count() > 0:
            return redirect(reverse('mybricks:detail', args=[str(existing[0].id)]))
        return handler

    def get_no_brickset_url(self):
        return reverse('sets:product_search_for_add')

    def get_context_data(self, **kwargs):
        context = super(MyBrickCreateView, self).get_context_data(**kwargs)
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
                messages.success(self.request, 'You successfully added a brick.', extra_tags='My Bricks')
        return super(MyBrickCreateView, self).form_valid(form)


class MyBrickUpdateView(LoginRequiredMixin, UserFormKwargsMixin, UpdateView):
    model = MyBrick
    form_class = MyBrickForm
    template_name = 'mybricks/mybrick_form.html'
    context_object_name = 'mybrick'

    def get_context_data(self, **kwargs):
        context = super(MyBrickUpdateView, self).get_context_data(**kwargs)
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
            messages.success(self.request, 'You brick is just updated', extra_tags='My Bricks')
        return super(MyBrickUpdateView, self).form_valid(form)


class MyBrickSoldView(LoginRequiredMixin, UserFormKwargsMixin, UpdateView):
    model = MyBrick
    form_class = MyBrickForm
    template_name = 'mybricks/mybrick_sold_form.html'
    context_object_name = 'mybrick'

    def get_context_data(self, **kwargs):
        context = super(MyBrickSoldView, self).get_context_data(**kwargs)
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
            messages.success(self.request, 'You brick is just updated', extra_tags='My Bricks')
        return super(MyBrickSoldView, self).form_valid(form)
