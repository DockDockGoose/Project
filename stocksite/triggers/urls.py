from django.urls import path, include
from .views.setBuyAmountView import SetBuyAmountView
from .views.setBuyTriggerView import SetBuyTriggerView
from .views.cancelSetBuyView import CancelSetBuyView
from .views.setSellAmountView import SetSellAmountView
from .views.setSellTriggerView import SetSellTriggerView
from .views.cancelSetSellView import CancelSetSellView

urlpatterns = [
    path('setbuyamount/', SetBuyAmountView.as_view()),
    path('setbuytrigger/', SetBuyTriggerView.as_view()),
    path('cancelsetbuy/', CancelSetBuyView.as_view()),
    path('setsellamount/', SetSellAmountView.as_view()),
    path('setselltrigger/', SetSellTriggerView.as_view()),
    path('cancelsetsell/', CancelSetSellView.as_view()),
    # path('', include(router.urls)),
]