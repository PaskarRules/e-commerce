from django.conf.urls import url
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from store.controller.account import auth

from . import views
from . import views_ajax


urlpatterns = [
    path('register/', auth.registerPage, name="register"),
    path('login/', auth.loginPage, name="login"),
    path('logout/', auth.logoutUser, name="logout"),

    path('user/', views.userPage, name="user-page"),
    path('cancel_order/', views.cancelOrder, name="cncl-order"),
    path('account/', views.accountSettings, name="account"),

    path('', views.store, name="store"),
    path('category/<slug:slug>/', views.categories, name="category"),
    path('product/product-<int:pk>/', views.product, name="product"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),

    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),

    path('ajax/order-<int:pk>', views_ajax.ajax_get_order_info, name="ajax_get_order_info"),

    path('pay-view<int:pk>/', views.PayView.as_view(), name='pay_view'),
    path('pay-callback/', views.PayCallbackView.as_view(), name='pay_callback'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
