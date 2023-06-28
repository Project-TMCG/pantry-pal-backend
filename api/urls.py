from django.urls import path
from .views import get_recipe

urlpatterns = [
    path('recipes/<int:id>/', get_recipe)
]