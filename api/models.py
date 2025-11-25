from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    artikul = models.CharField(max_length=11)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    card_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    unit = models.CharField(max_length=50, default='шт')  # шт, кг, литр и т.д.
    is_active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name


class Promotion(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='promotions/', null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'promotions'

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'product']

    @property
    def total_price(self):
        return self.product.price * self.quantity


# Добавляем в модель Order
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтвержден'),
        ('preparing', 'Готовится'),
        ('delivering', 'Доставляется'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'Наличными'),
        ('card', 'Картой'),
    ]

    DELIVERY_TIME_CHOICES = [
        ('asap', 'Как можно быстрее'),
        ('schedule', 'Выбрать дату и время'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Адрес доставки (выбирается из сохраненных адресов)
    delivery_address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True)

    # Время получения
    delivery_time_option = models.CharField(max_length=20, choices=DELIVERY_TIME_CHOICES, default='asap')
    scheduled_delivery_time = models.DateTimeField(null=True, blank=True)

    # Комментарий
    comment = models.TextField(blank=True)

    # Способ оплаты
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')

    # Суммы (пользователь вводит)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Сумма заказа
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Доставка
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Итого (order_amount + delivery_fee)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Автоматически рассчитываем итоговую сумму
        self.total_amount = self.order_amount + self.delivery_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.user.phone_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=200)
    house = models.CharField(max_length=10)
    building = models.CharField(max_length=10, blank=True)
    entrance = models.CharField(max_length=10, blank=True)
    floor = models.CharField(max_length=10, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'addresses'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.street}, {self.house}"


class Location(models.Model):
    address = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=100, default='Круглосуточно')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'locations'

    def __str__(self):
        return self.address


class BonusCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bonus_card')
    card_number = models.CharField(max_length=16, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'bonus_cards'

    def __str__(self):
        return f"Card {self.card_number}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def str(self):
        return f"{self.user} - {self.product.name}"