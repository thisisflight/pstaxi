from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Q, Prefetch, F, Case, When, IntegerField, Avg
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (ListView, DetailView, CreateView,
                                  UpdateView, DeleteView, TemplateView)
from django.views.generic.edit import ProcessFormView

from motorpool.models import Brand, Favorite, Auto, AutoReview, AutoRent
from utils.cache import CacheMixin
from .forms import (BrandCreationForm, BrandUpdateForm,
                    AutoFormSet, BrandAddToFavoriteForm, AutoReviewForm, AutoRentForm, AutoFilterForm)


@require_POST
def set_paginate_view(request):
    request.session['brand_list_paginate_by'] = request.POST.get('item_count', 0)
    return HttpResponseRedirect(reverse_lazy('motorpool:brand_list'))


class BrandCreateView(LoginRequiredMixin, CreateView):
    model = Brand
    template_name = 'motorpool/brand_create.html'
    form_class = BrandCreationForm
    success_url = reverse_lazy('motorpool:brand_list')

    def form_valid(self, form):
        messages.success(self.request, 'Новый бренд создан успешно')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class BrandUpdateView(UpdateView):
    model = Brand
    template_name = 'motorpool/brand_update.html'
    form_class = BrandUpdateForm


class BrandDeleteView(DeleteView):
    model = Brand
    template_name = 'motorpool/brand_delete.html'
    success_url = reverse_lazy('motorpool:brand_list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Бренд {self.object} удален')
        return result


class BrandList(ListView):
    model = Brand
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand_number'] = Brand.objects.count()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-pk')

    def get_paginate_by(self, queryset):
        paginate_by = super().get_paginate_by(queryset)
        if 'brand_list_paginate_by' in self.request.session:
            paginate_value = self.request.session['brand_list_paginate_by']
            if paginate_value.isdigit():
                paginate_by = paginate_value
        return paginate_by


class BrandDetailView(CacheMixin, DetailView):
    model = Brand

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cars'] = self.object.cars.all()
        context['favorite_form'] = BrandAddToFavoriteForm(initial={'user': self.request.user, 'brand': self.object})
        return context


class AutoCreateView(LoginRequiredMixin, ProcessFormView, TemplateView):

    template_name = 'motorpool/auto_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = get_object_or_404(Brand, pk=self.kwargs.get('brand_pk', ''))
        if self.request.method == 'POST':
            formset = AutoFormSet(self.request.POST, self.request.FILES, instance=brand)
        else:
            formset = AutoFormSet(instance=brand)
        context['formset'] = formset
        return context

    def post(self, request, *args, **kwargs):
        brand = get_object_or_404(Brand, pk=kwargs.get('brand_pk', ''))
        formset = AutoFormSet(request.POST, request.FILES, instance=brand)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(brand.get_absolute_url())
        return super().get(request, *args, **kwargs)


class BrandAddToFavoriteView(LoginRequiredMixin, CreateView):
    model = Favorite
    form_class = BrandAddToFavoriteForm

    def get_success_url(self):
        return self.object.brand.get_absolute_url()

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        brand = form.cleaned_data.get('brand', None)
        if not brand:
            brand = get_object_or_404(Brand, pk=form.data.get('brand'))
        redirect_url = brand.get_absolute_url() if brand else reverse_lazy('motorpool:brand_list')
        return HttpResponseRedirect(redirect_url)

    def form_valid(self, form):
        messages.success(self.request, f'Бренд {form.cleaned_data["brand"]} добавлен в избранное')
        return super().form_valid(form)


def auto_list(request):
    whens = [
        When(pts__engine_volume__gt=2000, then=0.2),
        When(pts__engine_volume__gt=1600, then=0.1),
    ]

    cars_qs = Auto.objects.select_related('pts').annotate(
        tax=F('pts__engine_volume') * Case(*whens,
                                           default=0,
                                           output_field=IntegerField()
                                           ))

    prefetch_all_cars = Prefetch('cars', queryset=cars_qs.all(), to_attr='all_cars_list')
    prefetch_new_cars = Prefetch('cars', queryset=cars_qs.filter(year__gt=2010), to_attr='new_cars_list')
    prefetch_old_cars = Prefetch('cars', queryset=cars_qs.filter(year__lt=2010), to_attr='old_cars_list')
    qs = Brand.objects.prefetch_related(prefetch_all_cars, prefetch_new_cars, prefetch_old_cars).annotate(
        car_count=Count('cars'),
        total_engine_power=Sum('cars__pts__engine_power'),
        new_cars=Count('cars', Q(cars__year__gt=2010)),
        old_cars=Count('cars', Q(cars__year__lt=2010))
    )
    return render(request, 'motorpool/auto_list.html', {'object_list': qs})


class AutoDetailView(CacheMixin, DetailView):
    model = Auto
    template_name = 'motorpool/auto_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.select_related('user')
        context['review_form'] = AutoReviewForm(initial={'user': self.request.user, 'auto': self.object})
        context['rent_form'] = AutoRentForm(initial={'user': self.request.user, 'auto': self.object})
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('brand').annotate(review_count=Count('reviews'), rate=Avg('reviews__rate'))
        return qs


class AutoSendReview(CreateView):
    model = AutoReview
    form_class = AutoReviewForm

    def get_success_url(self):
        return self.object.auto.get_absolute_url()

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(form.get_redirect_url())


class AutoRentView(CreateView):
    model = AutoRent
    form_class = AutoRentForm

    def get_success_url(self):
        return self.object.auto.get_absolute_url()

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(form.get_redirect_url())

    def form_valid(self, form):
        messages.success(self.request, f'Вы успешно забронировали автомобиль!')
        return super().form_valid(form)


class AutoListView(ListView):
    model = Auto
    template_name = 'motorpool/auto_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.object_list.count()
        context['filter_form'] = AutoFilterForm(self.request.GET)
        is_filter_used = bool(self.request.GET)
        if is_filter_used:
            context['query'] = '&'.join(['='.join(item) for item in self.request.GET.items()])
        context['is_filter_used'] = is_filter_used
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = AutoFilterForm(self.request.GET)
        if form.is_valid():
            filter_brand = form.cleaned_data['brand']
            filter_class = form.cleaned_data['auto_class']
            filter_options = form.cleaned_data['options']
            if filter_brand:
                queryset = queryset.filter(brand=filter_brand)
            if filter_class:
                queryset = queryset.filter(auto_class__in=filter_class)
            if filter_options:
                for option in filter_options:
                    queryset = queryset.filter(options__in=[option])
        queryset = queryset.select_related('brand').annotate(review_count=Count('reviews'), rate=Avg('reviews__rate'))
        return queryset
