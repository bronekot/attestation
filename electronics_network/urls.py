from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SupplierViewSet

router = DefaultRouter()
router.register(r"suppliers", SupplierViewSet)
# router.register(r"products", ProductViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
