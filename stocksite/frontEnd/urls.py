from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('viewStocks', views.viewStocks),
    path('viewTransactions', views.viewTransactions),
    path('viewMyTransactions', views.viewMyTransactions),
    path('transaction/<int:transactionNu>', views.viewIndividualTransaction),
    path('purchaseStock/<int:stockId>', views.purchaseStockView),
    path('confirmPurchase/', views.confirmPurchaseStock),
    path('confirmPurchase/confirmed/', views.processPurchase),
    path('sellStock/<str:stockSymbol>', views.sellStock),
    path('past_prices_chart/<int:stockId>', views.past_prices_chart, name='past_prices_chart'),
]