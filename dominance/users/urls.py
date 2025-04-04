from django.urls import path

from users.views import mpesa_confirmation


urlpatterns = [
    path("payment/confirmation", mpesa_confirmation, name="mpesa_confirmation"),
]
