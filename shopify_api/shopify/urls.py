from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [
    path("products/", ProductView.as_view(), name="product-list"),
    path("update/inventory/", UpdateInventory.as_view(), name="update-inventory"),
    path("products/search/", SemanticSearchAPIView.as_view(), name="semantic_search"),
    path("products/insights/", ProductsInsights.as_view(), name="insights")
]