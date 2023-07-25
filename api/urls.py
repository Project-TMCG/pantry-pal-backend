from django.urls import path
from .views import fetchRecipes

urlpatterns = [
    path('recipes/', fetchRecipes)
]