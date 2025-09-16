from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import F
from decimal import Decimal
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django_filters.views import FilterView
from .filters import ProductFilter # Этот файл еще не создан, но будет создан позже
from .forms import ProductForm, ProductImageForm, CategoryForm, ShopForm, TagForm, OrderForm, OrderItemForm
from .models import Product, Category, Shop, Tag, ProductImage, User, Location, UserLocation, PageCategory, Page, Order, OrderItem, Cart, CartItem
from .services.product_service import ProductService # Импортируем сервис
from django.forms import inlineformset_factory

# Аутентификация перенесена в products/views/auth_views.py

# Главная страница и список товаров
def index(request):
    """Главная страница с товарами в стиле Ozon"""
    products = Product.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related('images', 'tags')
    categories = Category.objects.all()[:12]
    
    # Фильтрация по категории
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Поиск
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Пагинация
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Получаем корневые категории для мегаменю
    root_categories = Category.objects.filter(
        parent__isnull=True, 
        is_active=True, 
        show_in_megamenu=True
    ).order_by('sort_order', 'slug')
    
    context = {
        'products': products,
        'categories': categories,
        'root_categories': root_categories,
        'catalog_categories': root_categories,  # Для мегаменю
        'search_query': search_query,
    }
    return render(request, 'index_ozon.html', context)


def category_view(request, category_slug):
    """Страница категории в стиле Ozon"""
    category = get_object_or_404(Category, slug=category_slug)
    
    # Получаем товары категории
    products = Product.objects.filter(
        category=category, 
        is_active=True
    ).select_related('seller', 'category').prefetch_related('images', 'tags', 'shops', 'characteristics')
    
    # Получаем все категории для навигации
    categories = Category.objects.filter(is_active=True).prefetch_related('children')
    
    # Фильтрация и поиск
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Сортировка
    sort_by = request.GET.get('sort', 'popularity')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:  # popularity
        products = products.order_by('-views_count', '-reviews_count')
    
    # Пагинация
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Подкатегории (если есть)
    subcategories = Category.objects.filter(parent=category, is_active=True) if hasattr(category, 'parent') else []
    
    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'subcategories': subcategories,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'category_ozon.html', context)

class ProductListView(FilterView):
    model = Product
    template_name = 'index.html'
    context_object_name = 'products'
    paginate_by = 12
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('images', 'category', 'seller', 'tags')
        query = self.request.GET.get('q')
        if query:
            search_query = SearchQuery(query)
            queryset = queryset.annotate(
                rank=SearchRank(F('search_vector'), search_query)
            ).filter(search_vector=search_query).order_by('-rank')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        context['current_language'] = translation.get_language()
        return context

# Страница детали товара
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail_ozon.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # Увеличиваем счетчик просмотров
        obj.views_count = F('views_count') + 1
        obj.save(update_fields=['views_count'])
        obj.refresh_from_db() # Обновляем объект после сохранения
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['images'] = product.images.all()
        context['is_favorite'] = self.request.user.is_authenticated and product.favorited_by.filter(pk=self.request.user.pk).exists()
        
        # Похожие товары
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(pk=product.pk)[:4]
        context['related_products'] = related_products
        
        return context

@login_required
def add_to_favorites(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user.favorites.filter(pk=product.pk).exists():
        request.user.favorites.remove(product)
        messages.info(request, _(f"Товар '{product.name}' удален из избранного."))
    else:
        request.user.favorites.add(product)
        messages.success(request, _(f"Товар '{product.name}' добавлен в избранное."))
    return redirect('product_detail', pk=pk)

# Миксины для проверки ролей
class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'manager'

    def handle_no_permission(self):
        messages.error(self.request, _("У вас нет прав для доступа к этой странице."))
        return redirect('index')

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, _("У вас нет прав для доступа к этой странице."))
        return redirect('index')

# Фронтенд-админка для менеджеров
class ManagerDashboardView(ManagerRequiredMixin, ListView):
    model = Product
    template_name = 'manager_dashboard.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        # Менеджер видит только товары своих магазинов
        if self.request.user.role == 'manager':
            return Product.objects.filter(shops__in=self.request.user.shops.all()).distinct()
        return Product.objects.all() # Администратор видит все

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь можно добавить аналитику для менеджера
        # Например, количество просмотров товаров, добавления в избранное
        return context

class ProductCreateView(ManagerRequiredMixin, SuccessMessageMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('manager_dashboard')
    success_message = _("Товар успешно создан!")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['images_formset'] = ProductForm.images(self.request.POST, self.request.FILES)
        else:
            data['images_formset'] = ProductForm.images()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        images_formset = context['images_formset']
        if images_formset.is_valid():
            self.object = form.save()
            images_formset.instance = self.object
            images_formset.save()
            messages.success(self.request, self.success_message)
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

class ProductUpdateView(ManagerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('manager_dashboard')
    success_message = _("Товар успешно обновлен!")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['images_formset'] = ProductForm.images(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['images_formset'] = ProductForm.images(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        images_formset = context['images_formset']
        if images_formset.is_valid():
            self.object = form.save()
            images_formset.instance = self.object
            images_formset.save()
            messages.success(self.request, self.success_message)
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

class ProductDeleteView(ManagerRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('manager_dashboard')
    success_message = _("Товар успешно удален!")

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

# Представления для управления категориями, магазинами, тегами (для администраторов)
class CategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = 'manager_dashboard.html' # Можно создать отдельный шаблон
    context_object_name = 'categories'

class CategoryCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'product_form.html' # Можно использовать общий шаблон формы
    success_url = reverse_lazy('category_list')
    success_message = _("Категория успешно создана!")

class CategoryUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('category_list')
    success_message = _("Категория успешно обновлена!")

class CategoryDeleteView(AdminRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Category
    template_name = 'product_confirm_delete.html' # Можно использовать общий шаблон подтверждения удаления
    success_url = reverse_lazy('category_list')
    success_message = _("Категория успешно удалена!")

class ShopListView(AdminRequiredMixin, ListView):
    model = Shop
    template_name = 'manager_dashboard.html'
    context_object_name = 'shops'

class ShopCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Shop
    form_class = ShopForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('shop_list')
    success_message = _("Магазин успешно создан!")

class ShopUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Shop
    form_class = ShopForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('shop_list')
    success_message = _("Магазин успешно обновлен!")

class ShopDeleteView(AdminRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Shop
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('shop_list')
    success_message = _("Магазин успешно удален!")

class TagListView(AdminRequiredMixin, ListView):
    model = Tag
    template_name = 'manager_dashboard.html'
    context_object_name = 'tags'

class TagCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('tag_list')
    success_message = _("Тег успешно создан!")

class TagUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('tag_list')
    success_message = _("Тег успешно обновлен!")

class TagDeleteView(AdminRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Tag
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('tag_list')
    success_message = _("Тег успешно удален!")

# AJAX для добавления/удаления из избранного
@login_required
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user.favorites.filter(pk=product.pk).exists():
        request.user.favorites.remove(product)
        is_favorite = False
        message = _(f"Товар '{product.name}' удален из избранного.")
    else:
        request.user.favorites.add(product)
        is_favorite = True
        message = _(f"Товар '{product.name}' добавлен в избранное.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite, 'message': message})
    else:
        messages.info(request, message)
        return redirect('product_detail', pk=pk)

# AJAX для фильтрации товаров (бесконечная прокрутка)
def product_filter_ajax(request):
    products = ProductService.get_filtered_products(request.GET)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    html = render_to_string('products/includes/product_list.html', {'page_obj': page_obj}, request=request)
    return JsonResponse({'html': html, 'has_next': page_obj.has_next()})


# View для тестирования локации
def test_location_view(request):
    """Тестовая страница для проверки работы локации"""
    locations = Location.objects.filter(is_active=True)
    current_location = getattr(request, 'user_location', None)

    context = {
        'locations': locations,
        'current_location': current_location,
    }
    return render(request, 'test_location.html', context)

def product_detail(request, product_id):
    """Детальная страница товара"""
    product = get_object_or_404(Product, id=product_id)
    
    # Увеличиваем счетчик просмотров
    product.views_count = F('views_count') + 1
    product.save(update_fields=['views_count'])
    
    # Получаем похожие товары из той же категории
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'product_detail.html', context)


def page_list_view(request, category_slug=None):
    """Список страниц по категориям"""
    categories = PageCategory.objects.filter(is_active=True)
    
    if category_slug:
        category = get_object_or_404(PageCategory, slug=category_slug, is_active=True)
        pages = Page.objects.filter(category=category, is_active=True, is_published=True)
        context = {
            'category': category,
            'pages': pages,
            'categories': categories,
        }
        return render(request, 'pages/category.html', context)
    else:
        context = {
            'categories': categories,
        }
        return render(request, 'pages/index.html', context)


def page_detail_view(request, slug):
    """Детальная страница"""
    page = get_object_or_404(Page, slug=slug, is_active=True, is_published=True)
    categories = PageCategory.objects.filter(is_active=True)
    
    context = {
        'page': page,
        'categories': categories,
    }
    return render(request, 'pages/detail.html', context)


# Представления для оформления заказа
@login_required
def checkout_view(request):
    """Страница оформления заказа"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product').prefetch_related('product__images')
    except Cart.DoesNotExist:
        cart_items = CartItem.objects.none()
        messages.warning(request, _("Ваша корзина пуста"))
        return redirect('cart')
    
    if not cart_items.exists():
        messages.warning(request, _("Ваша корзина пуста"))
        return redirect('cart')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = form.save(commit=False)
            order.user = request.user
            order.payment_method = form.cleaned_data['payment_method']
            order.delivery_method = form.cleaned_data['delivery_method']
            
            # Рассчитываем общую сумму
            total_amount = sum(item.total_price for item in cart_items)
            order.total_amount = total_amount
            
            # Добавляем стоимость доставки
            if order.delivery_method == 'courier':
                order.shipping_cost = Decimal('300.00')  # 300 рублей за курьерскую доставку
            elif order.delivery_method == 'post':
                order.shipping_cost = Decimal('150.00')  # 150 рублей за почтовую доставку
            else:  # pickup
                order.shipping_cost = Decimal('0.00')  # Бесплатно при самовывозе
            
            order.total_amount += order.shipping_cost
            order.save()
            
            # Создаем позиции заказа
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.final_price,
                    total_price=cart_item.total_price
                )
            
            # Очищаем корзину
            cart_items.delete()
            
            messages.success(request, _("Заказ успешно оформлен! Номер заказа: {}").format(order.order_number))
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'cart': cart,
    }
    return render(request, 'checkout.html', context)


@login_required
def order_detail_view(request, order_id):
    """Детальная страница заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.select_related('product').prefetch_related('product__images')
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'order_detail.html', context)


@login_required
def order_list_view(request):
    """Список заказов пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'order_list.html', context)


@login_required
def order_tracking_view(request, order_id):
    """Отслеживание заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Статусы заказа с описаниями
    status_descriptions = {
        'pending': _('Заказ ожидает подтверждения'),
        'confirmed': _('Заказ подтвержден и готовится к отправке'),
        'processing': _('Заказ обрабатывается'),
        'shipped': _('Заказ отправлен'),
        'delivered': _('Заказ доставлен'),
        'cancelled': _('Заказ отменен'),
    }
    
    context = {
        'order': order,
        'status_description': status_descriptions.get(order.status, _('Неизвестный статус')),
    }
    return render(request, 'order_tracking.html', context)