from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from crispy_forms.bootstrap import FormActions
from .models import Product, ProductImage, Category, Shop, Tag, Order, OrderItem, Review, PromoCode

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Кастомная форма регистрации пользователя"""
    email = forms.EmailField(required=True, label=_("Email"))
    first_name = forms.CharField(max_length=30, required=True, label=_("Имя"))
    last_name = forms.CharField(max_length=30, required=True, label=_("Фамилия"))
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial='user',
        label=_("Роль")
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'role',
            'password1',
            'password2',
            FormActions(
                Submit('submit', _('Зарегистрироваться'), css_class='btn btn-primary')
            )
        )

class CustomAuthenticationForm(AuthenticationForm):
    """Кастомная форма входа"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            FormActions(
                Submit('submit', _('Войти'), css_class='btn btn-primary')
            )
        )

class ProductForm(forms.ModelForm):
    """Форма для товара"""
    class Meta:
        model = Product
        fields = ['price', 'discount_price', 'currency', 'category', 'seller', 'tags', 'stock_quantity', 'is_active']
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('price', css_class='form-group col-md-6 mb-0'),
                Column('discount_price', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('currency', css_class='form-group col-md-6 mb-0'),
                Column('stock_quantity', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'category',
            'seller',
            'tags',
            'is_active',
            FormActions(
                Submit('submit', _('Сохранить'), css_class='btn btn-primary')
            )
        )

class ProductImageForm(forms.ModelForm):
    """Форма для изображения товара"""
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary', 'order']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'image',
            'alt_text',
            Row(
                Column('is_primary', css_class='form-group col-md-6 mb-0'),
                Column('order', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', _('Сохранить'), css_class='btn btn-primary')
            )
        )

class CategoryForm(forms.ModelForm):
    """Форма для категории"""
    class Meta:
        model = Category
        fields = ['slug', 'icon', 'parent', 'is_active', 'sort_order', 'show_in_megamenu']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('slug', css_class='form-group col-md-6 mb-0'),
                Column('icon', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'parent',
            Row(
                Column('is_active', css_class='form-group col-md-6 mb-0'),
                Column('sort_order', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'show_in_megamenu',
            FormActions(
                Submit('submit', _('Сохранить'), css_class='btn btn-primary')
            )
        )

class ShopForm(forms.ModelForm):
    """Форма для магазина"""
    class Meta:
        model = Shop
        fields = ['latitude', 'longitude', 'phone', 'email', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('latitude', css_class='form-group col-md-6 mb-0'),
                Column('longitude', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'is_active',
            FormActions(
                Submit('submit', _('Сохранить'), css_class='btn btn-primary')
            )
        )

class TagForm(forms.ModelForm):
    """Форма для тега"""
    class Meta:
        model = Tag
        fields = ['color']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'color',
            FormActions(
                Submit('submit', _('Сохранить'), css_class='btn btn-primary')
            )
        )

class OrderForm(forms.ModelForm):
    """Форма для заказа"""
    PAYMENT_METHOD_CHOICES = [
        ('card', _('Банковская карта')),
        ('cash', _('Наличные при получении')),
        ('bank_transfer', _('Банковский перевод')),
    ]
    
    DELIVERY_METHOD_CHOICES = [
        ('courier', _('Курьерская доставка')),
        ('post', _('Почтовая доставка')),
        ('pickup', _('Самовывоз')),
    ]
    
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, label=_("Способ оплаты"))
    delivery_method = forms.ChoiceField(choices=DELIVERY_METHOD_CHOICES, label=_("Способ доставки"))
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'notes']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'shipping_address',
            Row(
                Column('payment_method', css_class='form-group col-md-6 mb-0'),
                Column('delivery_method', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'notes',
            FormActions(
                Submit('submit', _('Оформить заказ'), css_class='btn btn-primary')
            )
        )

class OrderItemForm(forms.ModelForm):
    """Форма для позиции заказа"""
    class Meta:
        model = OrderItem
        fields = ['quantity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'quantity',
            FormActions(
                Submit('submit', _('Обновить'), css_class='btn btn-primary')
            )
        )

class ReviewForm(forms.ModelForm):
    """Форма для отзыва"""
    class Meta:
        model = Review
        fields = ['rating', 'title', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'rating',
            'title',
            'text',
            FormActions(
                Submit('submit', _('Отправить отзыв'), css_class='btn btn-primary')
            )
        )

class PromoCodeForm(forms.ModelForm):
    """Форма для промокода"""
    class Meta:
        model = PromoCode
        fields = ['code', 'discount_type', 'discount_value', 'min_order_amount', 'max_uses', 'valid_from', 'valid_until', 'is_active']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'code',
            Row(
                Column('discount_type', css_class='form-group col-md-6 mb-0'),
                Column('discount_value', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('min_order_amount', css_class='form-group col-md-6 mb-0'),
                Column('max_uses', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('valid_from', css_class='form-group col-md-6 mb-0'),
                Column('valid_until', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'is_active',
            FormActions(
                Submit('submit', _('Сохранить'), css_class='btn btn-primary')
            )
        )

# Inline formsets
ProductImageFormSet = forms.inlineformset_factory(
    Product, ProductImage, 
    form=ProductImageForm, 
    extra=1, 
    can_delete=True
)