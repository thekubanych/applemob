from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'home', HomeViewSet, basename='home')
router.register(r'purchases', PurchasesViewSet, basename='purchases')
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'locations', LocationViewSet)
router.register(r'favorites', FavoriteViewSet, basename='favorites')
router.register(r'bonus-cards', BonusCardViewSet, basename='bonuscard')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'promotions', PromotionViewSet)

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),

    # Новые endpoints для страниц адресов
    path('address-pages/<str:page_type>/', AddressPagesView.as_view(), name='address-pages'),
    path('check-address/', CheckAddressView.as_view(), name='check-address'),
]