from django.conf import settings
from django.http import HttpResponse
import requests

if settings.DEBUG:
    API_KEY=settings.API_KEY

# Create your views here.
def get_recipe(request, id=None):
    url=f'https://api.spoonacular.com/recipes/complexSearch?includeIngredients=tomato,cheese&apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return HttpResponse(data)