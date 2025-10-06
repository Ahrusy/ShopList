from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.db.models import F, Count
from decimal import Decimal
from django.db import models
# PostgreSQL search imports (conditionally imported where needed)
# from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django_filters.views import FilterView
from .filters import ProductFilter # Этот файл еще не создан, но будет создан позже
from .forms import ProductForm, ProductImageForm, CategoryForm, ShopForm, TagForm, OrderForm, OrderItemForm, TaskForm, MoodTrackingForm
from .models import Product, Category, Shop, Tag, ProductImage, User, Location, UserLocation, PageCategory, Page, Order, OrderItem, Cart, CartItem, Banner, ProductBanner, Task, MoodTracking
# from .services.product_service import ProductService # Импортируем сервис
from django.forms import inlineformset_factory

# Аутентификация перенесена в products/views/auth_views.py

# Главная страница и список товаров
def index(request):
    """Главная страница с товарами в стиле Ozon"""
    products = Product.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related('images', 'tags')
    categories = Category.objects.all()[:12]
    banners = Banner.objects.filter(is_active=True).order_by('sort_order')
    
    # Товарные баннеры для слайдера
    from .models import ProductBanner
    product_banners = ProductBanner.objects.filter(
        is_active=True
    ).order_by('sort_order')[:8]
    
    # Фильтрация по категории
    category_param = request.GET.get('category')
    is_main_page = not category_param  # Главная страница, если нет параметра category
    
    
    if category_param:
        # Убираем возможные суффиксы типа :1
        category_param = category_param.split(':')[0]
        
        # Пытаемся найти категорию по ID или slug
        try:
            # Если это число, ищем по ID
            category_id = int(category_param)
            products = products.filter(category_id=category_id)
        except ValueError:
            # Если не число, ищем по slug
            products = products.filter(category__slug=category_param)
    
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
        is_active=True
    ).order_by('sort_order', 'name')
    
    # Если это страница категории, перенаправляем на правильный URL категории
    if not is_main_page and category_param:
        from django.shortcuts import redirect
        from django.urls import reverse
        try:
            category = Category.objects.get(slug=category_param)
            # Перенаправляем на URL категории
            return redirect('category', category_slug=category.slug)
        except Category.DoesNotExist:
            # Если категория не найдена, продолжаем с обычным шаблоном
            pass
    
    # Главная страница
    context = {
        'products': products,
        'categories': categories,
        'root_categories': root_categories,
        'catalog_categories': root_categories,  # Для мегаменю
        'search_query': search_query,
        'is_main_page': is_main_page,
        'category_param': category_param,
        'banners': banners if is_main_page else [],
        'slider_products': product_banners if is_main_page else [],
    }
    return render(request, 'index_ozon.html', context)


@require_http_methods(["GET"])
def load_more_products(request):
    """AJAX endpoint для загрузки следующих страниц товаров"""
    page = request.GET.get('page', 1)
    search_query = request.GET.get('q', '')
    category_param = request.GET.get('category', '')
    
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1
    
    # Получаем товары (такая же логика как в index)
    products = Product.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related('images', 'tags')
    
    # Фильтрация по категории
    if category_param:
        category_param = category_param.split(':')[0]
        try:
            if category_param.isdigit():
                category = Category.objects.get(id=category_param)
            else:
                category = Category.objects.get(slug=category_param)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            pass
    
    # Поиск
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Сортировка
    products = products.order_by('-views_count', '-reviews_count')
    
    # Пагинация
    paginator = Paginator(products, 20)
    try:
        products_page = paginator.get_page(page)
    except:
        return JsonResponse({'error': 'Invalid page'}, status=400)
    
    # Рендерим HTML для товаров
    products_html = render_to_string('products/includes/product_cards.html', {
        'products': products_page
    })
    
    return JsonResponse({
        'html': products_html,
        'has_next': products_page.has_next(),
        'next_page': products_page.next_page_number() if products_page.has_next() else None,
        'current_page': page,
        'total_pages': paginator.num_pages
    })


def category_view(request, category_slug):
    """Страница категории в стиле Ozon с расширенной функциональностью"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    
    # Получаем товары категории и всех подкатегорий
    category_ids = [category.id]
    all_subcategories = category.get_all_children()
    category_ids.extend([subcat.id for subcat in all_subcategories])
    
    products = Product.objects.filter(
        category_id__in=category_ids, 
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
            Q(tags__name__icontains=search_query) |
            Q(brand__icontains=search_query)
        ).distinct()
    
    # Фильтрация по цене
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass
    
    # Фильтрация по бренду
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand__icontains=brand)
    
    # Фильтрация по рейтингу
    min_rating = request.GET.get('min_rating')
    if min_rating:
        try:
            products = products.filter(rating__gte=float(min_rating))
        except ValueError:
            pass
    
    # Фильтрация по наличию
    in_stock = request.GET.get('in_stock')
    if in_stock == '1':
        products = products.filter(stock_quantity__gt=0)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'popularity')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating', '-reviews_count')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    else:  # popularity
        products = products.order_by('-views_count', '-reviews_count', '-created_at')
    
    # Пагинация
    per_page = int(request.GET.get('per_page', 20))
    if per_page not in [12, 20, 40, 60]:
        per_page = 20
    
    paginator = Paginator(products, per_page)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    # Подкатегории (прямые дочерние)
    subcategories = Category.objects.filter(
        parent=category, 
        is_active=True
    ).order_by('sort_order', 'name')
    
    # Построение breadcrumbs
    breadcrumbs = []
    current_category = category
    while current_category:
        breadcrumbs.insert(0, current_category)
        current_category = current_category.parent
    
    # Получаем уникальные бренды для фильтра
    available_brands = products.values_list('brand', flat=True).distinct().exclude(brand='')
    available_brands = [brand for brand in available_brands if brand]
    
    # Статистика по ценам для фильтра
    price_stats = products.aggregate(
        min_price=models.Min('price'),
        max_price=models.Max('price')
    )
    
    context = {
        'category': category,
        'products': products_page,
        'categories': categories,
        'subcategories': subcategories,
        'breadcrumbs': breadcrumbs,
        'search_query': search_query,
        'sort_by': sort_by,
        'per_page': per_page,
        'available_brands': available_brands,
        'price_stats': price_stats,
        'current_filters': {
            'price_min': price_min,
            'price_max': price_max,
            'brand': brand,
            'min_rating': min_rating,
            'in_stock': in_stock,
        },
        'total_products': paginator.count,
    }
    return render(request, 'category_ozon.html', context)


def catalog_view(request):
    """Главная страница каталога с категориями всех уровней"""
    # Получаем корневые категории
    root_categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    ).prefetch_related('children__children').order_by('sort_order', 'name')
    
    # Популярные категории (с наибольшим количеством товаров)
    popular_categories = Category.objects.filter(
        is_active=True,
        has_products=True
    ).order_by('-products_count')[:8]
    
    # Новые товары
    new_products = Product.objects.filter(
        is_active=True
    ).select_related('category', 'seller').prefetch_related('images').order_by('-created_at')[:12]
    
    # Популярные товары
    popular_products = Product.objects.filter(
        is_active=True
    ).select_related('category', 'seller').prefetch_related('images').order_by('-views_count', '-reviews_count')[:12]
    
    context = {
        'root_categories': root_categories,
        'popular_categories': popular_categories,
        'new_products': new_products,
        'popular_products': popular_products,
    }
    return render(request, 'catalog.html', context)


def category_products_ajax(request, category_slug):
    """AJAX endpoint для загрузки товаров категории"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    
    # Получаем товары категории и всех подкатегорий
    category_ids = [category.id]
    all_subcategories = category.get_all_children()
    category_ids.extend([subcat.id for subcat in all_subcategories])
    
    products = Product.objects.filter(
        category_id__in=category_ids, 
        is_active=True
    ).select_related('seller', 'category').prefetch_related('images')
    
    # Применяем фильтры (аналогично category_view)
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__name__icontains=search_query) |
            Q(brand__icontains=search_query)
        ).distinct()
    
    # Фильтрация по цене
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass
    
    # Сортировка
    sort_by = request.GET.get('sort', 'popularity')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating', '-reviews_count')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:  # popularity
        products = products.order_by('-views_count', '-reviews_count')
    
    # Пагинация
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 20))
    
    paginator = Paginator(products, per_page)
    try:
        products_page = paginator.get_page(page)
    except:
        return JsonResponse({'error': 'Invalid page'}, status=400)
    
    # Рендерим HTML для товаров
    products_html = render_to_string('products/includes/product_cards.html', {
        'products': products_page
    })
    
    return JsonResponse({
        'html': products_html,
        'has_next': products_page.has_next(),
        'has_previous': products_page.has_previous(),
        'next_page': products_page.next_page_number() if products_page.has_next() else None,
        'previous_page': products_page.previous_page_number() if products_page.has_previous() else None,
        'current_page': int(page),
        'total_pages': paginator.num_pages,
        'total_products': paginator.count
    })

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
            # Проверяем, используем ли мы PostgreSQL (только PostgreSQL поддерживает SearchVector)
            from django.conf import settings
            db_engine = settings.DATABASES['default']['ENGINE']
            
            if 'postgresql' in db_engine:
                # Используем полнотекстовый поиск PostgreSQL
                from django.contrib.postgres.search import SearchQuery, SearchRank
                search_query = SearchQuery(query)
                queryset = queryset.annotate(
                    rank=SearchRank(F('search_vector'), search_query)
                ).filter(search_vector=search_query).order_by('-rank')
            else:
                # Для других баз данных (например, SQLite) используем простой поиск по названию и описанию
                from django.db import models
                queryset = queryset.filter(
                    models.Q(name__icontains=query) | models.Q(description__icontains=query)
                )
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


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mood_trackings'] = MoodTracking.objects.filter(user=self.request.user)[:5]  # Last 5 mood trackings
        return context


class TaskCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')
    success_message = _("Задача успешно создана!")
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Sync with Google Calendar if user has token
        if self.request.user.google_calendar_token:
            try:
                calendar_service = GoogleCalendarService(self.request.user)
                if calendar_service.is_available():
                    event_id = calendar_service.create_event(self.object)
                    if event_id:
                        self.object.google_calendar_event_id = event_id
                        self.object.save()
                        messages.info(self.request, _("Задача синхронизирована с Google Calendar."))
                    else:
                        messages.warning(self.request, _("Не удалось синхронизировать задачу с Google Calendar."))
            except Exception as e:
                messages.warning(self.request, _("Ошибка синхронизации с Google Calendar: {}").format(str(e)))
        
        return response


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')
    success_message = _("Задача успешно обновлена!")
    
    def test_func(self):
        task = self.get_object()
        return task.user == self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Sync with Google Calendar if user has token
        if self.request.user.google_calendar_token:
            try:
                calendar_service = GoogleCalendarService(self.request.user)
                if calendar_service.is_available():
                    success = calendar_service.update_event(self.object)
                    if success:
                        messages.info(self.request, _("Изменения синхронизированы с Google Calendar."))
                    else:
                        messages.warning(self.request, _("Не удалось синхронизировать изменения с Google Calendar."))
            except Exception as e:
                messages.warning(self.request, _("Ошибка синхронизации с Google Calendar: {}").format(str(e)))
        
        return response


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')
    success_message = _("Задача успешно удалена!")
    
    def test_func(self):
        task = self.get_object()
        return task.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        
        # Delete from Google Calendar if synced
        if task.google_calendar_event_id and request.user.google_calendar_token:
            try:
                calendar_service = GoogleCalendarService(request.user)
                if calendar_service.is_available():
                    calendar_service.delete_event(task)
            except Exception as e:
                messages.warning(request, _("Ошибка удаления из Google Calendar: {}").format(str(e)))
        
        return super().delete(request, *args, **kwargs)


class MoodTrackingCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = MoodTracking
    form_class = MoodTrackingForm
    template_name = 'mood/mood_form.html'
    success_url = reverse_lazy('task_list')  # Redirect to task list after mood tracking
    success_message = _("Настроение успешно записано!")
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class MoodTrackingListView(LoginRequiredMixin, ListView):
    model = MoodTracking
    template_name = 'mood/mood_list.html'
    context_object_name = 'mood_trackings'
    paginate_by = 20
    
    def get_queryset(self):
        return MoodTracking.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add mood statistics for chart
        mood_data = MoodTracking.objects.filter(user=self.request.user).values('mood').annotate(count=Count('mood')).order_by('mood')
        
        # Prepare data for chart
        mood_labels = []
        mood_values = []
        mood_colors = []
        
        mood_color_map = {
            'very_happy': '#4ade80',  # green
            'happy': '#a3e635',       # light green
            'neutral': '#fde047',     # yellow
            'sad': '#f97316',         # orange
            'very_sad': '#ef4444',    # red
        }
        
        for item in mood_data:
            mood_labels.append(MoodTracking._meta.get_field('mood').choices_dict[item['mood']])
            mood_values.append(item['count'])
            mood_colors.append(mood_color_map.get(item['mood'], '#cccccc'))
        
        context['mood_chart_data'] = {
            'labels': mood_labels,
            'values': mood_values,
            'colors': mood_colors,
        }
        
        return context

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
    product.refresh_from_db()  # Обновляем объект после сохранения
    
    # Получаем похожие товары из той же категории
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:5]
    
    context = {
        'product': product,
        'related_products': related_products,
        'images': product.images.all(),
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


def product_banners_management(request):
    """Страница управления товарными баннерами"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
    
    return render(request, 'admin/product_banners_management.html')
import requests
from django.conf import settings
from django.utils import timezone

# from .services.google_calendar_service import GoogleCalendarService

@staff_member_required
def product_banners_management(request):
    """
    Управление товарными баннерами
    """
    from .models import ProductBanner
    
    banners = ProductBanner.objects.all().order_by('sort_order', '-created_at')
    
    context = {
        'banners': banners,
        'title': 'Управление товарными баннерами'
    }
    
    return render(request, 'admin/product_banners_management.html', context)