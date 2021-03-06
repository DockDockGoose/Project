"""stocksite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from frontEnd import views

urlpatterns = [
    path('api/stocks/', include('stocks.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/triggers/', include('triggers.urls')),
    path('api/', include('transactions.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('api/', include('frontEndStocks.urls')),
    path('api/', include('prevPrices.urls')),
    path('frontEnd/', include('frontEnd.urls')),
    #path('frontEnd/viewTransactions', views.viewTransactions),
    path('admin/', admin.site.urls),
    # # Additionally, we include login URLs for the browsable API.
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
