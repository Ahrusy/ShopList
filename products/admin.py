from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Category, Shop, Tag, Product, ProductImage, ProductCharacteristic,
    Seller, Order, OrderItem, Review, Cart, CartItem, Commission,
    Location, UserLocation, PageCategory, Page, PromoCode, Notification, Banner, ProductBanner, StaticPage
)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Персональная информация'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Права доступа'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups', 'user_permissions', 'favorites')


class SubcategoryInline(admin.TabularInline):
    """Inline для редактирования подкатегорий"""
    model = Category
    fk_name = 'parent'
    extra = 0
    fields = ('name', 'slug', 'icon', 'sort_order', 'is_active', 'show_in_megamenu')
    readonly_fields = ('category_level', 'path', 'products_count')
    verbose_name = _("Подкатегория")
    verbose_name_plural = _("Подкатегории")
    
    def get_queryset(self, request):
        """Ограничиваем только прямыми дочерними категориями"""
        qs = super().get_queryset(request)
        return qs.order_by('sort_order', 'name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('get_tree_display', 'name', 'category_level', 'products_count', 'sort_order', 'is_active', 'show_in_megamenu', 'created_at')
    list_filter = ('is_active', 'show_in_megamenu', 'category_level', 'created_at')
    search_fields = ('name', 'slug', 'description')
    list_editable = ('sort_order', 'is_active', 'show_in_megamenu')
    ordering = ('category_level', 'sort_order', 'name')
    inlines = [SubcategoryInline]
    actions = ['create_subcategories', 'update_products_count', 'preview_mega_menu']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'slug', 'description', 'icon')
        }),
        (_('Иерархия'), {
            'fields': ('parent', 'category_level', 'path'),
            'classes': ('collapse',)
        }),
        (_('Мега меню'), {
            'fields': ('mega_menu_image', 'mega_menu_description', 'featured_products'),
            'classes': ('collapse',)
        }),
        (_('Настройки'), {
            'fields': ('sort_order', 'is_active', 'show_in_megamenu', 'has_products', 'products_count')
        }),
    )
    
    readonly_fields = ('category_level', 'path', 'products_count', 'has_products')
    filter_horizontal = ('featured_products',)
    
    def get_tree_display(self, obj):
        """Отображает категорию с отступами для визуализации дерева"""
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * obj.category_level
        icon = '📁' if obj.get_children().exists() else '📄'
        return f'{indent}{icon} {obj.name}'
    get_tree_display.short_description = _('Структура категорий')
    get_tree_display.allow_tags = True
    
    def get_queryset(self, request):
        """Оптимизируем запросы и сортируем по иерархии"""
        qs = super().get_queryset(request)
        return qs.select_related('parent').prefetch_related('children', 'products')
    
    def create_subcategories(self, request, queryset):
        """Массовое действие для создания подкатегорий"""
        created_count = 0
        for category in queryset:
            try:
                subcategories = category.ensure_subcategories()
                created_count += len(subcategories)
            except Exception as e:
                self.message_user(request, f'Ошибка при создании подкатегорий для {category.name}: {str(e)}', level='ERROR')
        
        if created_count > 0:
            self.message_user(request, f'Создано {created_count} подкатегорий', level='SUCCESS')
        else:
            self.message_user(request, 'Подкатегории уже существуют или не могут быть созданы', level='INFO')
    
    create_subcategories.short_description = _('Создать подкатегории для выбранных категорий')
    
    def update_products_count(self, request, queryset):
        """Массовое действие для обновления счетчиков товаров"""
        updated_count = 0
        for category in queryset:
            old_count = category.products_count
            new_count = category.update_products_count()
            category.save()
            if old_count != new_count:
                updated_count += 1
        
        self.message_user(request, f'Обновлены счетчики для {updated_count} категорий', level='SUCCESS')
    
    update_products_count.short_description = _('Обновить счетчики товаров')
    
    def preview_mega_menu(self, request, queryset):
        """Предварительный просмотр мега меню"""
        if queryset.count() == 1:
            category = queryset.first()
            # Перенаправляем на страницу предварительного просмотра
            from django.shortcuts import redirect
            return redirect(f'/admin/products/category-preview/{category.id}/')
        else:
            self.message_user(request, 'Выберите только одну категорию для предварительного просмотра', level='WARNING')
    
    preview_mega_menu.short_description = _('Предварительный просмотр мега меню')
    
    def save_model(self, request, obj, form, change):
        """Переопределяем сохранение для обновления иерархии"""
        super().save_model(request, obj, form, change)
        # Обновляем счетчик товаров после сохранения
        obj.update_products_count()
        obj.save()
    
    class Media:
        css = {
            'all': ('admin/css/category_admin.css',)
        }
        js = ('admin/js/category_admin.js',)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('phone', 'email')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('color', 'created_at')
    search_fields = ('color',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductCharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'seller', 'price', 'discount_price', 'stock_quantity', 'rating', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'seller', 'created_at')
    search_fields = ('name', 'description', 'sku')
    inlines = [ProductImageInline, ProductCharacteristicInline]
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'description', 'category', 'seller', 'tags')
        }),
        (_('Цена и наличие'), {
            'fields': ('price', 'discount_price', 'stock_quantity', 'is_active')
        }),
        (_('Рейтинг и просмотры'), {
            'fields': ('rating', 'reviews_count', 'views_count')
        }),
        (_('Системная информация'), {
            'fields': ('sku', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('sku', 'rating', 'reviews_count', 'views_count', 'created_at', 'updated_at')


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'commission_rate', 'is_verified', 'rating', 'total_sales', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('company_name', 'user__username', 'user__email')
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('user', 'company_name', 'description')
        }),
        (_('Комиссия и статус'), {
            'fields': ('commission_rate', 'is_verified')
        }),
        (_('Статистика'), {
            'fields': ('rating', 'total_sales', 'total_revenue'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('rating', 'total_sales', 'total_revenue', 'created_at', 'updated_at')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'title', 'is_verified_purchase', 'is_moderated', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_moderated', 'created_at')
    search_fields = ('user__username', 'product__name', 'title', 'text')
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('user', 'product', 'order', 'rating', 'title', 'text')
        }),
        (_('Статус'), {
            'fields': ('is_verified_purchase', 'is_moderated')
        }),
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('total_items', 'total_price', 'created_at', 'updated_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__user__username', 'product__name')


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('seller', 'order', 'amount', 'rate', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('seller__company_name', 'order__order_number')
    readonly_fields = ('created_at',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'country', 'is_active', 'created_at')
    list_filter = ('is_active', 'country', 'created_at')
    search_fields = ('name', 'region', 'country')
    ordering = ('name',)


@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'is_auto_detected', 'created_at')
    list_filter = ('is_auto_detected', 'created_at')
    search_fields = ('user__username', 'location__name')
    ordering = ('-created_at',)


@admin.register(PageCategory)
class PageCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('sort_order', 'name')


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'is_published', 'sort_order', 'updated_at')
    list_filter = ('is_active', 'is_published', 'category', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'slug', 'category', 'content')
        }),
        (_('SEO'), {
            'fields': ('meta_description',)
        }),
        (_('Статус'), {
            'fields': ('is_active', 'is_published', 'sort_order')
        }),
    )
    ordering = ('category__sort_order', 'sort_order', 'title')


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_order_amount', 'used_count', 'is_active', 'valid_from', 'valid_until')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_until', 'created_at')
    search_fields = ('code',)
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('code', 'discount_type', 'discount_value')
        }),
        (_('Условия'), {
            'fields': ('min_order_amount', 'max_uses', 'valid_from', 'valid_until')
        }),
        (_('Статистика'), {
            'fields': ('used_count', 'is_active'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('used_count', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('user', 'type', 'title', 'message')
        }),
        (_('Статус'), {
            'fields': ('is_read',)
        }),
    )
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'banner_type', 'is_active', 'sort_order', 'created_at', 'updated_at')
    list_filter = ('banner_type', 'is_active', 'created_at')
    search_fields = ('title', 'subtitle')
    list_editable = ('is_active', 'sort_order')
    ordering = ('sort_order', '-created_at')
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'subtitle', 'image', 'link')
        }),
        (_('Настройки'), {
            'fields': ('banner_type', 'is_active', 'sort_order')
        }),
    )


@admin.register(ProductBanner)
class ProductBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'style', 'is_active', 'sort_order', 'button_text', 'created_at')
    list_filter = ('style', 'is_active', 'created_at')
    search_fields = ('title', 'subtitle', 'description')
    list_editable = ('is_active', 'sort_order', 'button_text')
    ordering = ('sort_order', '-created_at')
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'subtitle', 'description', 'image', 'link')
        }),
        (_('Стиль и дизайн'), {
            'fields': ('style', 'button_text', 'background_color', 'text_color')
        }),
        (_('Настройки'), {
            'fields': ('is_active', 'sort_order')
        }),
    )


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'slug', 'content')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'meta_description', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
        js = ('admin/js/textarea_resize.js',)