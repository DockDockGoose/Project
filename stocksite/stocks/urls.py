from django.urls import path, include
from .views.quoteView import QuoteView
from .views.buyView import BuyView
from .views.sellView import SellView
from .views.commitBuyView import CommitBuyView
from .views.commitSellView import CommitSellView
from .views.cancelBuyView import CancelBuyView
from .views.cancelSellView import CancelSellView

urlpatterns = [
    path('buy/', BuyView.as_view()),
    path('cancelbuy/', CancelBuyView.as_view()),
    path('cancelsell/', CancelSellView.as_view()),
    path('commitbuy/', CommitBuyView.as_view()),
    path('commitsell/', CommitSellView.as_view()),
    path('sell/', SellView.as_view()),
    path('quote/', QuoteView.as_view()),
    # path('', include(router.urls)),
]