from django.urls import path, include
from rest_framework import routers
from .views import StockViewSet

router = routers.DefaultRouter()
router.register(r'stocks', StockViewSet)

urlpatterns = router.urls