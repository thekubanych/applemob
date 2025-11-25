from rest_framework import serializers
from .models import *
from users.models import UserProfile

# Сначала определяем базовые сериализаторы
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderCreateSerializer(serializers.ModelSerializer):
    delivery_address_id = serializers.IntegerField(write_only=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'delivery_address_id',
            'delivery_time_option',
            'scheduled_delivery_time',
            'comment',
            'payment_method',
            'order_amount',
            'delivery_fee',
            'total_amount'
        ]

    def validate_delivery_address_id(self, value):
        # Проверяем что адрес принадлежит пользователю
        user = self.context['request'].user
        if not Address.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError("Адрес не найден")
        return value

class OrderListSerializer(serializers.ModelSerializer):
    delivery_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class BonusCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusCard
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    # read-only вложенный продукт для GET
    product = ProductSerializer(read_only=True)
    # поле для записи: принимаем id продукта
    product_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Favorite
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"detail": "Authentication required."})

        product_id = validated_data.pop('product_id', None)
        # также принимаем 'product' key (иногда фронт отправляет product)
        if product_id is None:
            product_id = request.data.get('product') or request.data.get('product_id')

        if not product_id:
            raise serializers.ValidationError({'product_id': 'This field is required.'})

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_id': 'Product not found.'})

        favorite, created = Favorite.objects.get_or_create(user=user, product=product)
        return favorite


# Serializer для истории покупок (Order -> frontend)
class PurchaseSerializer(serializers.ModelSerializer):
    address_text = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, source='total_amount')

    class Meta:
        model = Order
        fields = ('id', 'total_amount', 'address_text', 'created_at', 'status')

    def get_address_text(self, obj):
        if obj.delivery_address:
            return str(obj.delivery_address)
        # fallback
        primary = getattr(obj.user, 'addresses', None)
        if primary:
            p = primary.filter(is_primary=True).first()
            if p:
                return str(p)
        return ''