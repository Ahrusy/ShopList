from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
# from parler.models import TranslatableModel, TranslatedFields # Закомментировано


class ClientAccount(models.Model):
    """Отдельная модель клиента (не связана с Django admin)."""
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name=_("Телефон"))
    first_name = models.CharField(max_length=30, blank=True, verbose_name=_("Имя"))
    last_name = models.CharField(max_length=30, blank=True, verbose_name=_("Фамилия"))
    password = models.CharField(max_length=128, verbose_name=_("Пароль (хеш)"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        ordering = ['-created_at']

    def __str__(self):
        return self.email

class User(AbstractUser):
    """Кастомная модель пользователя"""
    ROLE_CHOICES = [
        ('user', _('Покупатель')),
        ('seller', _('Продавец')),
        ('manager', _('Менеджер')),
        ('admin', _('Администратор')),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name=_("Роль"))
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name=_("Телефон"))
    middle_name = models.CharField(max_length=30, blank=True, null=True, verbose_name=_("Отчество"))
    favorites = models.ManyToManyField('Product', related_name='favorited_by', blank=True, verbose_name=_("Избранные товары"))
    google_calendar_token = models.TextField(blank=True, null=True, verbose_name=_("Токен Google Calendar"))


class Task(models.Model):
    """Модель задачи пользователя"""
    PRIORITY_CHOICES = [
        ('low', _('Низкий')),
        ('medium', _('Средний')),
        ('high', _('Высокий')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('В ожидании')),
        ('in_progress', _('В процессе')),
        ('completed', _('Завершено')),
        ('cancelled', _('Отменено')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', verbose_name=_("Пользователь"))
    title = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name=_("Приоритет"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Статус"))
    due_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Дата выполнения"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))
    google_calendar_event_id = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("ID события в Google Calendar"))
    
    class Meta:
        verbose_name = _("Задача")
        verbose_name_plural = _("Задачи")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class MoodTracking(models.Model):
    """Модель отслеживания настроения пользователя"""
    MOOD_CHOICES = [
        ('very_happy', _('Очень радостное')),
        ('happy', _('Радостное')),
        ('neutral', _('Нейтральное')),
        ('sad', _('Грустное')),
        ('very_sad', _('Очень грустное')),
    ]
    
    # Create a dictionary for easy access to choices
    choices_dict = dict(MOOD_CHOICES)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_trackings', verbose_name=_("Пользователь"))
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, verbose_name=_("Настроение"))
    note = models.TextField(blank=True, verbose_name=_("Заметка"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    
    class Meta:
        verbose_name = _("Отслеживание настроения")
        verbose_name_plural = _("Отслеживания настроения")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_mood_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Category(models.Model): # Изменено с TranslatableModel
    """Модель категории товаров"""
    # translations = TranslatedFields( # Закомментировано
    name=models.CharField(max_length=100, default="", verbose_name=_("Название"))
    description=models.TextField(blank=True, verbose_name=_("Описание"))
    # ) # Закомментировано
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
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ['sort_order', 'slug']


class Shop(models.Model): # Изменено с TranslatableModel
    """Модель магазина"""
    # translations = TranslatedFields( # Закомментировано
    name=models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Название"))
    address=models.TextField(blank=True, null=True, verbose_name=_("Адрес"))
    city=models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Город"))
    # ) # Закомментировано
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
        ordering = ['phone']


class Tag(models.Model): # Изменено с TranslatableModel
    """Модель тега"""
    # translations = TranslatedFields( # Закомментировано
    name=models.CharField(max_length=50, unique=True, default="", verbose_name=_("Название"))
    # ) # Закомментировано
    color = models.CharField(max_length=7, default='#007bff', verbose_name=_("Цвет"))
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Тег")
        verbose_name_plural = _("Теги")
        ordering = ['color']


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


class Product(models.Model): # Изменено с TranslatableModel
    """Модель товара"""
    # translations = TranslatedFields( # Закомментировано
    name=models.CharField(max_length=255, default="", verbose_name=_("Название"))
    description=models.TextField(default="", verbose_name=_("Описание"))
    # ) # Закомментировано
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_("Цена со скидкой"))
    currency = models.CharField(max_length=3, default='RUB', verbose_name=_("Валюта"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name=_("Категория"))
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products', null=True, blank=True, verbose_name=_("Продавец"))
    shops = models.ManyToManyField(Shop, related_name='products', verbose_name=_("Магазины"))
    tags = models.ManyToManyField(Tag, blank=True, related_name='products', verbose_name=_("Теги"))
    sku = models.CharField(max_length=100, unique=True, blank=True, verbose_name=_("Артикул"))
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name=_("Количество на складе"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name=_("Рейтинг"))
    reviews_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество отзывов"))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество просмотров"))
    search_vector = SearchVectorField(null=True, verbose_name=_("Вектор поиска"))
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
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['rating']),
            models.Index(fields=['views_count']),
        ]


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
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
        ]


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


class PromoCode(models.Model):
    """Модель промокода"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', _('Процент')),
        ('fixed', _('Фиксированная сумма')),
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Код промокода"))
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, verbose_name=_("Тип скидки"))
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Размер скидки"))
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Минимальная сумма заказа"))
    max_uses = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Максимальное количество использований"))
    used_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество использований"))
    valid_from = models.DateTimeField(verbose_name=_("Действует с"))
    valid_until = models.DateTimeField(verbose_name=_("Действует до"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}%"
    
    def is_valid(self):
        """Проверяет, действителен ли промокод"""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.max_uses is None or self.used_count < self.max_uses)
        )
    
    def calculate_discount(self, order_amount):
        """Рассчитывает размер скидки для заказа"""
        if not self.is_valid() or order_amount < self.min_order_amount:
            return 0
        
        if self.discount_type == 'percentage':
            return (order_amount * self.discount_value) / 100
        else:  # fixed
            return min(self.discount_value, order_amount)
    
    class Meta:
        verbose_name = _("Промокод")
        verbose_name_plural = _("Промокоды")
        ordering = ['-created_at']


class Notification(models.Model):
    """Модель уведомления"""
    NOTIFICATION_TYPES = [
        ('order_created', _('Заказ создан')),
        ('order_confirmed', _('Заказ подтвержден')),
        ('order_shipped', _('Заказ отправлен')),
        ('order_delivered', _('Заказ доставлен')),
        ('order_cancelled', _('Заказ отменен')),
        ('review_added', _('Добавлен отзыв')),
        ('product_updated', _('Товар обновлен')),
        ('promo_code', _('Промокод')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications', verbose_name=_("Пользователь"))
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, verbose_name=_("Тип уведомления"))
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    message = models.TextField(verbose_name=_("Сообщение"))
    is_read = models.BooleanField(default=False, verbose_name=_("Прочитано"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        verbose_name = _("Уведомление")
        verbose_name_plural = _("Уведомления")
        ordering = ['-created_at']


# Сигналы
@receiver(post_save, sender=Product)
def update_product_search_vector(sender, instance, **kwargs):
    """Обновляет вектор поиска для товара"""
    # Проверяем, что это не рекурсивный вызов
    if not kwargs.get('update_fields') or 'search_vector' not in kwargs.get('update_fields', []):
        # Проверяем, используем ли мы PostgreSQL (только PostgreSQL поддерживает SearchVector)
        from django.conf import settings
        from django.db import transaction
        
        # Получаем тип базы данных
        db_engine = settings.DATABASES['default']['ENGINE']
        
        # Используем SearchVector только если это PostgreSQL
        if 'postgresql' in db_engine:
            with transaction.atomic():
                # Обновляем search_vector напрямую через QuerySet, чтобы избежать рекурсии
                Product.objects.filter(pk=instance.pk).update(
                    search_vector=SearchVector('name', 'description')
                )
        # Для других баз данных (например, SQLite) просто пропускаем обновление search_vector
        # Это предотвращает ошибку с to_tsvector в SQLite


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


class Favorite(models.Model):
    """Модель избранных товаров"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_items', verbose_name=_("Пользователь"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites', verbose_name=_("Товар"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата добавления"))
    
    class Meta:
        verbose_name = _("Избранное")
        verbose_name_plural = _("Избранное")
        unique_together = ['user', 'product']  # Один товар может быть в избранном у пользователя только один раз
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Banner(models.Model):
    """Модель рекламных баннеров"""
    BANNER_TYPE_CHOICES = [
        ('main', _('Главный баннер')),
        ('sidebar', _('Боковой баннер')),
        ('footer', _('Нижний баннер')),
        ('product', _('Товарный баннер')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    subtitle = models.CharField(max_length=300, blank=True, verbose_name=_("Подзаголовок"))
    image = models.ImageField(upload_to='banners/', verbose_name=_("Изображение"))
    link = models.URLField(blank=True, verbose_name=_("Ссылка"))
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPE_CHOICES, default='main', verbose_name=_("Тип баннера"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок сортировки"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Баннер")
        verbose_name_plural = _("Баннеры")
        ordering = ['sort_order', '-created_at']


class ProductBanner(models.Model):
    """Модель товарных баннеров для слайдера"""
    BANNER_STYLE_CHOICES = [
        ('discount', _('Скидка')),
        ('new', _('Новинка')),
        ('popular', _('Популярное')),
        ('premium', _('Премиум')),
        ('sale', _('Распродажа')),
        ('delivery', _('Доставка')),
    ]
    
    title = models.CharField(max_length=100, verbose_name=_("Заголовок"))
    subtitle = models.CharField(max_length=200, blank=True, verbose_name=_("Подзаголовок"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    image = models.ImageField(upload_to='product_banners/', verbose_name=_("Изображение"))
    link = models.URLField(blank=True, verbose_name=_("Ссылка"))
    style = models.CharField(max_length=20, choices=BANNER_STYLE_CHOICES, default='new', verbose_name=_("Стиль баннера"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок сортировки"))
    button_text = models.CharField(max_length=50, default='Подробнее', verbose_name=_("Текст кнопки"))
    background_color = models.CharField(max_length=7, default='#000000', verbose_name=_("Цвет фона"))
    text_color = models.CharField(max_length=7, default='#FFFFFF', verbose_name=_("Цвет текста"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Товарный баннер")
        verbose_name_plural = _("Товарные баннеры")
        ordering = ['sort_order', '-created_at']


@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    """Создает корзину для нового пользователя"""
    if created:
        Cart.objects.create(user=instance)


class StaticPage(models.Model):
    """Модель для статических страниц сайта"""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL-адрес')
    content = models.TextField(verbose_name='Содержимое')
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='Мета-описание')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Статическая страница'
        verbose_name_plural = 'Статические страницы'
        ordering = ['title']
    
    def __str__(self):
        return self.title