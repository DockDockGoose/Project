from django.urls import path, include
# from rest_framework import routers
from .views import BuyView, SellView, QuoteView, CommitBuyView

# router = routers.DefaultRouter()
# router.register(r'stocks', SharesViewSet, basename='stocks')

urlpatterns = [
    path('buy/', BuyView.as_view()),
    path('commitbuy/', CommitBuyView.as_view()),
    path('sell/', SellView.as_view()),
    path('quote/', QuoteView.as_view()),
    # path('', include(router.urls)),
]