from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r"^products/", ProductView.as_view(), name="product-list"),
    url(r"^update/inventory/", UpdateInventory.as_view(), name="update-inventory"),
]