from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, Field
from django.utils.translation import gettext_lazy as _
from .models import User, Product, Category, Shop, Tag, ProductImage


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_("Email"))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("Основная информация"),
                'username',
                'email',
                'password1',
                'password2',
            ),
            Submit('submit', _('Зарегистрироваться'), css_class='btn btn-primary')
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("Вход в систему"),
                'username',
                'password',
            ),
            Submit('submit', _('Войти'), css_class='btn btn-primary')
        )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount_price', 'category', 'seller', 'tags', 'stock_quantity', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("Основная информация"),
                'name',
                'description',
                'category',
                'seller',
            ),
            Fieldset(
                _("Цена и наличие"),
                'price',
                'discount_price',
                'stock_quantity',
                'is_active',
            ),
            Fieldset(
                _("Теги"),
                'tags',
            ),
            Submit('submit', _('Сохранить'), css_class='btn btn-primary')
        )

    @staticmethod
    def images():
        return forms.inlineformset_factory(
            Product, ProductImage,
            fields=['image', 'alt_text', 'is_primary', 'order'],
            extra=3,
            can_delete=True
        )


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary', 'order']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'slug', 'icon', 'parent', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("Основная информация"),
                'name',
                'description',
                'slug',
                'icon',
            ),
            Fieldset(
                _("Иерархия"),
                'parent',
            ),
            Fieldset(
                _("Статус"),
                'is_active',
            ),
            Submit('submit', _('Сохранить'), css_class='btn btn-primary')
        )


class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'address', 'city', 'latitude', 'longitude', 'phone', 'email', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("Основная информация"),
                'name',
                'address',
                'city',
            ),
            Fieldset(
                _("Контакты"),
                'phone',
                'email',
            ),
            Fieldset(
                _("Координаты"),
                'latitude',
                'longitude',
            ),
            Fieldset(
                _("Статус"),
                'is_active',
            ),
            Submit('submit', _('Сохранить'), css_class='btn btn-primary')
        )


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'color']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("Информация о теге"),
                'name',
                'color',
            ),
            Submit('submit', _('Сохранить'), css_class='btn btn-primary')
        )