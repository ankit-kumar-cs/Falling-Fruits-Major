from django.urls import path
from . import views
from .views import ProductView,ProductDetailView,CartView,OrderDetailView
urlpatterns = [
    path('',views.home_page, name="home"),
    path('working/',views.working,name="working"),
    path('register/',views.registration_view,name="register"),
    path('logout/',views.logout_view,name="logout"),
    path('login/',views.login_view,name="log-in"),
    path('accounts/login/',views.login_view,name="log-in"),
    path('profile/',views.profile_view,name='profile'),
    path('update-profile/',views.update_profile,name="update-profile"),
    path('product/',ProductView.as_view(),name="product"),
    path('product/<slug:slug>/',ProductDetailView.as_view(),name="product-detail"),
    path('cart/',views.CartView,name="cart"),
    path('add-to-cart/<slug:slug>/',views.add_to_cart,name='add-to-cart'),
    path('remove-from-cart/<slug:slug>/',views.remove_from_cart,name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug:slug>/',views.remove_single_item_from_cart,name='remove-single-from-cart'),
    path('checkout/',views.CheckoutView,name='checkout'),
    path('order/',OrderDetailView.as_view(),name='order-detail-view')
    #path('profile/update-profile/',views.update_profile,name="update_profile"),
]
