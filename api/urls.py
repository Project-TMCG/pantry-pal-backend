from django.urls import path
from .views import get_recipe

urlpatterns = [
    path('recipes/<slug:ingredients>/', get_recipe),
    path('recipes/<slug:ingredients>/<str:diet>', get_recipe)
]