from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginpage, name='login'),
    path('logout/', views.logoutuser, name='logout'),
    path('register/', views.register, name='register'),
    path('account/', views.account, name='account'),
    path('homepage/', views.homepage, name='homepage'),
    path('prod/<invID>/', views.prod, name='prod'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/', views.add_to_cart, name='add'),
    path('checkout/', views.generate_payment_link, name="checkout"),
    path('updatecart/', views.update_cart, name="update_cart"),
]

