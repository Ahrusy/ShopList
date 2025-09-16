from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


class User(AbstractUser):
    """Кастомная модель пользователя"""
    ROLE_CHOICES = [
        ('user', _('Покупатель')),
        ('seller', _('Продавец')),
        ('manager', _('Менеджер')),
        ('admin', _('Администратор')),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name=_("Роль"))
    favorites = models.ManyToManyField('Product', related_name='favorited_by', blank=True, verbose_name=_("Избранные товары"))

    def __str__(self):
        return self.username


class Category(models.Model):
    """Модель категории товаров"""
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("URL-адрес"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Иконка"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_("Родительская категория"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок сортировки"))
    show_in_megamenu = models.BooleanField(default=True, verbose_name=_("Показывать в мегаменю"))
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

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
        return list(self.children.filter(is_active=True).order_by('sort_order', 'name'))

    def get_children(self):
        """Возвращает дочерние категории"""
        return self.children.filter(is_active=True).order_by('sort_order', 'name')

    def get_all_children(self):
        """Возвращает все дочерние категории рекурсивно"""
        children = list(self.get_children())
        for child in children:
            children.extend(child.get_all_children())
        return children

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ['sort_order', 'name']


class Shop(models.Model):
    """Модель магазина"""
    name = models.CharField(max_length=255, verbose_name=_("Название"))
    address = models.TextField(verbose_name=_("Адрес"))
    city = models.CharField(max_length=100, verbose_name=_("Город"))
    latitude = models.FloatField(blank=True, null=True, verbose_name=_("Широта"))
    longitude = models.FloatField(blank=True, null=True, verbose_name=_("Долгота"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Телефон"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")
        ordering = ['name']


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Название"))
    color = models.CharField(max_length=7, default='#007bff', verbose_name=_("Цвет"))
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")
        ordering = ['name']


class Seller(models.Model):
    """Модель продавца"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile', verbose_name=_("Пользователь"))
    company_name = models.CharField(max_length=255, verbose_name=_("Название компании"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, verbose_name=_("Ставка комиссии (%)"))
    is_verified = models.BooleanField(default=False, verbose_name=_("Верифицирован"))
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name=_("Рейтинг"))
    total_sales = models.PositiveIntegerField(default=0, verbose_name=_("Всего продаж"))
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name=_("Общая выручка"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата регистрации"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name = _("Продавец")
        verbose_name_plural = _("Продавцы")
        ordering = ['-created_at']


class Product(models.Model):
    """Модель товара"""
    name = models.CharField(max_length=255, verbose_name=_("Название"))
    description = models.TextField(verbose_name=_("Описание"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_("Цена со скидкой"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name=_("Категория"))
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products', null=True, blank=True, verbose_name=_("Продавец"))
    tags = models.ManyToManyField(Tag, blank=True, related_name='products', verbose_name=_("Теги"))
    sku = models.CharField(max_length=100, unique=True, blank=True, verbose_name=_("Артикул"))
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name=_("Количество на складе"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name=_("Рейтинг"))
    reviews_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество отзывов"))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество просмотров"))
    # search_vector = SearchVectorField(blank=True, verbose_name=_("Вектор поиска"))
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

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
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering = ['-created_at']


class ProductCharacteristic(models.Model):
    """Модель характеристики товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics', verbose_name=_("Товар"))
    name = models.CharField(max_length=100, verbose_name=_("Название характеристики"))
    value = models.CharField(max_length=255, verbose_name=_("Значение"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return f"{self.name}: {self.value}"

    class Meta:
        verbose_name = _("Характеристика товара")
        verbose_name_plural = _("Характеристики товаров")
        ordering = ['name']


class ProductImage(models.Model):
    """Модель изображения товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_("Товар"))
    image = models.ImageField(upload_to='products/%Y/%m/%d/', verbose_name=_("Изображение"))
    alt_text = models.CharField(max_length=255, blank=True, verbose_name=_("Альтернативный текст"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Основное изображение"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return f"{self.product.name} - {self.alt_text or 'Изображение'}"

    class Meta:
        verbose_name = _("Изображение товара")
        verbose_name_plural = _("Изображения товаров")
        ordering = ['order', 'created_at']


class ProductCharacteristic(models.Model):
    """Модель характеристики товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics', verbose_name=_("Товар"))
    name = models.CharField(max_length=100, verbose_name=_("Название характеристики"))
    value = models.CharField(max_length=255, verbose_name=_("Значение"))
    unit = models.CharField(max_length=20, blank=True, verbose_name=_("Единица измерения"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))
    
    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"
    
    class Meta:
        verbose_name = _("Характеристика товара")
        verbose_name_plural = _("Характеристики товаров")
        ordering = ['order', 'name']


class Order(models.Model):
    """Модель заказа"""
    STATUS_CHOICES = [
        ('pending', _('Ожидает подтверждения')),
        ('confirmed', _('Подтвержден')),
        ('processing', _('В обработке')),
        ('shipped', _('Отправлен')),
        ('delivered', _('Доставлен')),
        ('cancelled', _('Отменен')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Ожидает оплаты')),
        ('paid', _('Оплачен')),
        ('failed', _('Ошибка оплаты')),
        ('refunded', _('Возвращен')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_("Пользователь"))
    order_number = models.CharField(max_length=20, unique=True, verbose_name=_("Номер заказа"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Статус"))
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name=_("Статус оплаты"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Общая сумма"))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Стоимость доставки"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Размер скидки"))
    shipping_address = models.TextField(verbose_name=_("Адрес доставки"))
    notes = models.TextField(blank=True, verbose_name=_("Примечания"))
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))
    
    def __str__(self):
        return f"Заказ {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Модель позиции заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_("Заказ"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Товар"))
    quantity = models.PositiveIntegerField(verbose_name=_("Количество"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена за единицу"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Общая цена"))
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _("Позиция заказа")
        verbose_name_plural = _("Позиции заказа")
        unique_together = ['order', 'product']


class Review(models.Model):
    """Модель отзыва"""
    RATING_CHOICES = [
        (1, _('1 звезда')),
        (2, _('2 звезды')),
        (3, _('3 звезды')),
        (4, _('4 звезды')),
        (5, _('5 звезд')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name=_("Пользователь"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name=_("Товар"))
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Заказ"))
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, verbose_name=_("Рейтинг"))
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    text = models.TextField(verbose_name=_("Текст отзыва"))
    is_verified_purchase = models.BooleanField(default=False, verbose_name=_("Подтвержденная покупка"))
    is_moderated = models.BooleanField(default=True, verbose_name=_("Прошел модерацию"))
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} звезд)"
    
    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")
        ordering = ['-created_at']
        unique_together = ['user', 'product']


class Cart(models.Model):
    """Модель корзины"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name=_("Пользователь"))
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))
    
    def __str__(self):
        return f"Корзина {self.user.username}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    class Meta:
        verbose_name = _("Корзина")
        verbose_name_plural = _("Корзины")


class CartItem(models.Model):
    """Модель позиции корзины"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name=_("Корзина"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Товар"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Количество"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата добавления"))
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.product.final_price * self.quantity
    
    class Meta:
        verbose_name = _("Позиция корзины")
        verbose_name_plural = _("Позиции корзины")
        unique_together = ['cart', 'product']


class Commission(models.Model):
    """Модель комиссии"""
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='commissions', verbose_name=_("Продавец"))
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='commissions', verbose_name=_("Заказ"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Сумма комиссии"))
    rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Ставка комиссии (%)"))
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата создания"))
    
    def __str__(self):
        return f"Комиссия {self.seller.company_name} - {self.amount} ₽"
    
    class Meta:
        verbose_name = _("Комиссия")
        verbose_name_plural = _("Комиссии")
        ordering = ['-created_at']


# Сигналы
# @receiver(post_save, sender=Product)
# def update_product_search_vector(sender, instance, **kwargs):
#     """Обновляет вектор поиска для товара"""
#     instance.search_vector = SearchVector('name', 'description')
#     instance.save(update_fields=['search_vector'])


@receiver(post_save, sender=Review)
def update_product_rating(sender, instance, **kwargs):
    """Обновляет рейтинг товара при добавлении отзыва"""
    if instance.is_moderated:
        product = instance.product
        reviews = product.reviews.filter(is_moderated=True)
        if reviews.exists():
            product.rating = reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
            product.reviews_count = reviews.count()
            product.save(update_fields=['rating', 'reviews_count'])


@receiver(post_save, sender=Order)
def create_commission(sender, instance, **kwargs):
    """Создает комиссию для продавца при подтверждении заказа"""
    if instance.status == 'confirmed' and instance.payment_status == 'paid':
        for item in instance.items.all():
            if item.product.seller:
                commission_amount = (item.total_price * item.product.seller.commission_rate) / 100
                Commission.objects.create(
                    seller=item.product.seller,
                    order=instance,
                    amount=commission_amount,
                    rate=item.product.seller.commission_rate
                )
                
                # Обновляем статистику продавца
                seller = item.product.seller
                seller.total_sales += item.quantity
                seller.total_revenue += item.total_price
                seller.save(update_fields=['total_sales', 'total_revenue'])


class Location(models.Model):
    """Модель локации"""
    name = models.CharField(max_length=100, verbose_name=_("Название города"))
    region = models.CharField(max_length=100, blank=True, verbose_name=_("Регион"))
    country = models.CharField(max_length=100, default='Россия', verbose_name=_("Страна"))
    latitude = models.FloatField(blank=True, null=True, verbose_name=_("Широта"))
    longitude = models.FloatField(blank=True, null=True, verbose_name=_("Долгота"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    
    def __str__(self):
        return f"{self.name}, {self.region}" if self.region else self.name
    
    class Meta:
        verbose_name = _("Локация")
        verbose_name_plural = _("Локации")
        ordering = ['name']


class UserLocation(models.Model):
    """Модель локации пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_locations', verbose_name=_("Пользователь"))
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name=_("Локация"))
    is_auto_detected = models.BooleanField(default=False, verbose_name=_("Автоматически определена"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата установки"))

    def __str__(self):
        return f"{self.user.username} - {self.location.name}"

    class Meta:
        verbose_name = _("Локация пользователя")
        verbose_name_plural = _("Локации пользователей")
        unique_together = ['user', 'location']


class PageCategory(models.Model):
    """Модель категории страниц"""
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    slug = models.SlugField(unique=True, verbose_name=_("URL"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок сортировки"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Категория страниц")
        verbose_name_plural = _("Категории страниц")
        ordering = ['sort_order', 'name']


class Page(models.Model):
    """Модель страницы"""
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    slug = models.SlugField(unique=True, verbose_name=_("URL"))
    content = models.TextField(verbose_name=_("Содержимое"))
    category = models.ForeignKey(PageCategory, on_delete=models.CASCADE, related_name='pages', verbose_name=_("Категория"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))
    is_published = models.BooleanField(default=True, verbose_name=_("Опубликована"))
    meta_description = models.CharField(max_length=300, blank=True, verbose_name=_("Meta описание"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок сортировки"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Страница")
        verbose_name_plural = _("Страницы")
        ordering = ['category__sort_order', 'sort_order', 'title']


@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    """Создает корзину для нового пользователя"""
    if created:
        Cart.objects.create(user=instance)