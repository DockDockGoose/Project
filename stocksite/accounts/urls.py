from django.urls import path, include
from django.contrib import admin
from .views import AccountListView, AddView

urlpatterns = [
    path('', AccountListView.as_view()),
    # TODO: Figure out how to make dynamic account urls using this
    # path('<slug:username>/', AccountView.as_view(), name='username'),
    path('add/', AddView.as_view()),
    path('rest-auth/', include('rest_auth.urls')),
]
