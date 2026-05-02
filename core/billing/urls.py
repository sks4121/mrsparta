from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('plans/', views.plans_pricing, name='plans-pricing'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/process/', views.payment_process, name='payment-process'),
    path('payment/success/', views.payment_success, name='payment-success'),
    path('payment/error/', views.payment_error, name='payment-error'),
    path('subscription/manage/', views.subscription_manage, name='subscription-manage'),
    path('invoices/', views.invoice_list, name='invoice-list'),
    path('invoice/<int:pk>/', views.invoice_detail, name='invoice-detail'),
]
