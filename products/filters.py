import django_filters
from django import forms
from parler.forms import TranslatableModelForm
from .models import Product, Category, Shop, Tag
from django.utils.translation import gettext_lazy as _

class ProductFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category__translations__name',
        label=_('Категория'),
        empty_label=_('Все категории')
    )
    shops = django_filters.ModelMultipleChoiceFilter(
        queryset=Shop.objects.all(),
        field_name='shops__translations__name',
        label=_('Магазины'),
        widget=forms.CheckboxSelectMultiple
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__translations__name',
        label=_('Теги'),
        widget=forms.CheckboxSelectMultiple
    )
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label=_('Цена от'))
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label=_('Цена до'))

    class Meta:
        model = Product
        fields = ['category', 'shops', 'tags', 'price_min', 'price_max']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['category'].empty_label = _('Все категории')
        self.form.fields['shops'].empty_label = _('Все магазины')
        self.form.fields['tags'].empty_label = _('Все теги')