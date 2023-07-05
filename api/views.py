from django.conf import settings
from django.http import JsonResponse
import requests

API_KEY = ''

if settings.DEBUG:
    API_KEY=settings.API_KEY

def assembleUrl(queryParams):
    url=f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}'

# Create your views here.
def get_recipe(request, ingredients):
    
    response = requests.get(url)
    data = response.json()
    return JsonResponse(data)