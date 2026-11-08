from django.contrib import admin
from django.urls import path
from energy import views
from energy import payments
urlpatterns=[
 path('admin/',admin.site.urls),
 path('',views.home,name='home'),
 path("about/", views.about, name="about"),
 path("how-it-works/", views.how_it_works, name="how_it_works"),
 path('api/catalog/',views.catalog,name='catalog'),
 path('api/calculate/',views.calculate,name='calculate'),
 path('api/quote/',views.create_quote,name='create_quote'),
 path('quote/<int:quote_id>/pdf/',views.quote_pdf,name='quote_pdf'),
 path("privacy-policy/",views.privacy_policy,name="privacy_policy"),
 path(
    "quote/<int:quote_id>/pay/",
    payments.initialize_payment,
    name="initialize_payment"
),
path(
    "payment/callback/",
    payments.payment_callback,
    name="payment_callback"
),
path(
    "payment/webhook/",
    payments.paystack_webhook,
    name="paystack_webhook"
),
]
