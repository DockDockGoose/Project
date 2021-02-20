from django.urls import path, include
from rest_framework import routers
from .views import TransactionViewSet

router = routers.DefaultRouter()
router.register(r'transactions', TransactionViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = router.urls