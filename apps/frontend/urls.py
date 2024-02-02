from django.urls import path
from apps.frontend.views import *

app_name = 'frontend'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('category/<slug>/', CategoryView.as_view(), name='category'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', AddToCartView.as_view(), name='add-to-cart'),
    path('add_coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug:slug>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('remove-single-item-from-cart/<slug:slug>/', RemoveSingleItemFromCartView.as_view(), name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('profile/', ProfileEditView.as_view(), name='profile'),
    path('update-profile-pic/', UpdateProfilePic.as_view(), name='update-profile-pic'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('page/<str:category>/<slug:slug>/', FooterPagesView.as_view(), name='page'),


]
