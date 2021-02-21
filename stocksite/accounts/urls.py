from django.urls import path, include
from django.contrib import admin
from .views import AccountListView

urlpatterns = [
    path('', AccountListView.as_view()),
    path('rest-auth/', include('rest_auth.urls')),
]
