from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Category, Shop, Tag, Product, ProductImage, ProductCharacteristic,
    Seller, Order, OrderItem, Review, Cart, CartItem, Commission,
    Location, UserLocation, PageCategory, Page
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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'level', 'sort_order', 'is_active', 'show_in_megamenu', 'created_at')
    list_filter = ('is_active', 'show_in_megamenu', 'parent', 'created_at')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('sort_order', 'is_active', 'show_in_megamenu')
    ordering = ('sort_order', 'name')
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'slug', 'description', 'icon')
        }),
        (_('Иерархия'), {
            'fields': ('parent',)
        }),
        (_('Настройки'), {
            'fields': ('sort_order', 'is_active', 'show_in_megamenu')
        }),
    )
    
    def level(self, obj):
        return obj.level
    level.short_description = _('Уровень')
    level.admin_order_field = 'parent'


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'city', 'created_at')
    search_fields = ('name', 'address', 'city', 'phone', 'email')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    search_fields = ('name',)


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