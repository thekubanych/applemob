import os
import random
import base64
from io import BytesIO
from collections import OrderedDict

from django.db.models import Q
from django.contrib.auth import authenticate
from django.utils.dateparse import parse_date

from rest_framework import viewsets, status, mixins, generics, permissions
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

import qrcode

from core import settings
from .models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema


# ================================
# Корневой API
# ================================
@swagger_auto_schema(method='get', tags=['Root'])
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'категории': reverse('category-list', request=request, format=format),
        'продукты': reverse('product-list', request=request, format=format),
        'тележка': reverse('cart-list', request=request, format=format),
        'приказы': reverse('order-list', request=request, format=format),
        'адреса': reverse('address-list', request=request, format=format),
        'избранное': reverse('favorites-list', request=request, format=format),
        'местоположения': reverse('location-list', request=request, format=format),
        'бонус-карты': reverse('bonuscard-list', request=request, format=format),
        'уведомления': reverse('notification-list', request=request, format=format),
        'рекламныеакции': reverse('promotion-list', request=request, format=format),
        'главнаястраница': reverse('home-list', request=request, format=format),
        'историяпокупок': reverse('purchases-list', request=request, format=format),
    })


# ================================
# Категории
# ================================
class CategoryViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Categories'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Categories'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


# ================================
# Продукты
# ================================
class ProductViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Products'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Products'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Products'])
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.GET.get('q', '')
        category_id = request.GET.get('category')
        queryset = self.queryset
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ================================
# Локации
# ================================
class LocationViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Locations'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Locations'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


# ================================
# Акции
# ================================
class PromotionViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = PromotionSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Promotions'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Promotions'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


# ================================
# Бонус-карты
# ================================
class BonusCardViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = BonusCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BonusCard.objects.filter(user=self.request.user)

    @swagger_auto_schema(tags=['BonusCards'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['BonusCards'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


# ================================
# Уведомления
# ================================
class NotificationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @swagger_auto_schema(tags=['Notifications'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Notifications'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Notifications'])
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})


# ================================
# Корзина
# ================================
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Cart'])
    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['Cart'])
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['Cart'])
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        cart = Cart.objects.get(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
        except CartItem.DoesNotExist:
            return Response({'error': 'Товар не найден в корзине'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response(serializer.data)


# ================================
# Заказы
# ================================
class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create_order':
            return OrderCreateSerializer
        return OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @swagger_auto_schema(tags=['Orders'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Orders'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Orders'])
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        delivery_address = Address.objects.get(
            id=serializer.validated_data['delivery_address_id'], user=request.user
        )
        order = Order.objects.create(
            user=request.user,
            delivery_address=delivery_address,
            delivery_time_option=serializer.validated_data['delivery_time_option'],
            scheduled_delivery_time=serializer.validated_data.get('scheduled_delivery_time'),
            comment=serializer.validated_data.get('comment', ''),
            payment_method=serializer.validated_data['payment_method'],
            order_amount=serializer.validated_data['order_amount'],
            delivery_fee=serializer.validated_data['delivery_fee'],
        )
        return Response({
            'message': 'Заказ успешно оформлен! Менеджер скоро свяжется с вами.',
            'order': OrderListSerializer(order).data
        }, status=status.HTTP_201_CREATED)


# ================================
# Адреса
# ================================
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressPagesView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Addresses'])
    def get(self, request, page_type):
        addresses = Address.objects.filter(user=request.user)
        if page_type == 'empty':
            return Response({'page_type': 'empty', 'message': 'Здесь будут храниться ваши адреса', 'has_addresses': False})
        elif page_type == 'list':
            serializer = AddressSerializer(addresses, many=True)
            return Response({'page_type': 'list', 'addresses': serializer.data, 'has_addresses': addresses.exists()})
        elif page_type == 'new':
            return Response({
                'page_type': 'new',
                'fields': {
                    'street': {'required': True, 'label': 'Улица*'},
                    'house': {'required': True, 'label': 'Дом*'},
                    'building': {'required': False, 'label': 'Корпус'},
                    'entrance': {'required': False, 'label': 'Подъезд'},
                    'floor': {'required': False, 'label': 'Этаж'}
                }
            })
        return Response({'error': 'Неизвестный тип страницы'}, status=400)


class CheckAddressView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Addresses'])
    def get(self, request):
        has_addresses = Address.objects.filter(user=request.user).exists()
        return Response({'has_addresses': has_addresses})


# ================================
# Избранное
# ================================
class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    @swagger_auto_schema(tags=['Favorites'])
    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product") or request.data.get("product_id")
        if not product_id:
            return Response({"error": "product (id) is required"}, status=400)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        serializer = FavoriteSerializer(favorite, context={'request': request})
        return Response(serializer.data, status=201 if created else 200)
class HomeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        bonus = 0
        card_number = None
        qr_base64 = None

        if hasattr(user, "bonus_card"):
            bonus = user.bonus_card.balance
            card_number = user.bonus_card.card_number

            # QR code from card_number
            qr = qrcode.make(card_number)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        promotions = Promotion.objects.filter(is_active=True)
        products = Product.objects.filter(is_active=True).order_by('-id')[:10]

        return Response({
            "bonus": bonus,
            "card_number": card_number,
            "qr_code": qr_base64,
            "promotions": PromotionSerializer(promotions, many=True).data,
            "hot_products": ProductSerializer(products, many=True).data,
        })
class PurchasesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
