from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


class User(AbstractUser):
    """Кастомная модель пользователя"""
    ROLE_CHOICES = [
        ('user', 'Покупатель'),
        ('seller', 'Продавец'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name="Роль")
    favorites = models.ManyToManyField('Product', related_name='favorited_by', blank=True, verbose_name="Избранные товары")

    def __str__(self):
        return self.username


class Category(models.Model):
    """Упрощенная модель категории товаров"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-адрес")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Родительская категория")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    show_in_megamenu = models.BooleanField(default=True, verbose_name="Показывать в мегаменю")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    @property
    def level(self):
        """Возвращает уровень вложенности категории"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    @property
    def is_root(self):
        """Проверяет, является ли категория корневой"""
        return self.parent is None

    @property
    def children_list(self):
        """Возвращает дочерние категории как список для шаблонов"""
        return list(self.children.filter(is_active=True).order_by('sort_order', 'slug'))

    def get_children(self):
        """Возвращает дочерние категории"""
        return self.children.filter(is_active=True).order_by('sort_order', 'slug')

    def get_all_children(self):
        """Возвращает все дочерние категории рекурсивно"""
        children = list(self.get_children())
        for child in children:
            children.extend(child.get_all_children())
        return children

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['sort_order', 'slug']


class Seller(models.Model):
    """Модель продавца"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile', verbose_name="Пользователь")
    company_name = models.CharField(max_length=255, verbose_name="Название компании")
    description = models.TextField(blank=True, verbose_name="Описание")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, verbose_name="Ставка комиссии (%)")
    is_verified = models.BooleanField(default=False, verbose_name="Верифицирован")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Рейтинг")
    total_sales = models.PositiveIntegerField(default=0, verbose_name="Всего продаж")
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Общая выручка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name = "Продавец"
        verbose_name_plural = "Продавцы"
        ordering = ['-created_at']


class Product(models.Model):
    """Упрощенная модель товара"""
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Цена со скидкой")
    currency = models.CharField(max_length=3, default='RUB', verbose_name="Валюта")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="Категория")
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products', null=True, blank=True, verbose_name="Продавец")
    sku = models.CharField(max_length=100, unique=True, blank=True, verbose_name="Артикул")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Рейтинг")
    reviews_count = models.PositiveIntegerField(default=0, verbose_name="Количество отзывов")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        """Возвращает финальную цену (со скидкой или обычную)"""
        return self.discount_price if self.discount_price else self.price
    
    @property
    def discount_percentage(self):
        """Возвращает процент скидки"""
        if self.discount_price and self.price:
            return ((self.price - self.discount_price) / self.price) * 100
        return 0
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"PRD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['rating']),
            models.Index(fields=['views_count']),
        ]


class ProductImage(models.Model):
    """Модель изображения товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Товар")
    image = models.ImageField(upload_to='products/%Y/%m/%d/', verbose_name="Изображение")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Альтернативный текст")
    is_primary = models.BooleanField(default=False, verbose_name="Основное изображение")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.product.name} - {self.alt_text or 'Изображение'}"

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ['order', 'created_at']


class ProductCharacteristic(models.Model):
    """Модель характеристики товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics', verbose_name="Товар")
    name = models.CharField(max_length=100, verbose_name="Название характеристики")
    value = models.CharField(max_length=255, verbose_name="Значение")
    unit = models.CharField(max_length=20, blank=True, verbose_name="Единица измерения")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    
    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"
    
    class Meta:
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товаров"
        ordering = ['order', 'name']