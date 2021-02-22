from django.urls import path, include
from rest_framework import routers
from .views import StockViewSet, BuyView

router = routers.DefaultRouter()
router.register(r'stocks', StockViewSet)

urlpatterns = [
    path('buy/', BuyView.as_view()),
    path('', include(router.urls)),
]