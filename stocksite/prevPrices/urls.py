from django.urls import path, include
from rest_framework import routers
from .views import PrevPricesViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'prevPrices', PrevPricesViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = router.urls