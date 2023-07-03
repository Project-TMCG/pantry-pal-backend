from django.shortcuts import render
from django.http import HttpResponse
import requests

API_KEY = ''

# Create your views here.
def get_recipe(request, id=None):
    url=f'https://api.spoonacular.com/recipes/findByIngredients?ingredients=onions&apiKey={API_KEY}&number=1&limitLicense=true&ranking=1&ignorePantry=false&sortDirection=asc&addRecipeInformation=true&instructionsRequired=true&maxReadyTime=5'
    response = requests.get(url)
    data = response.json()
    return HttpResponse(data)