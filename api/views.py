from django.conf import settings
from django.http import JsonResponse
import requests

API_KEY = ''

if settings.DEBUG:
    API_KEY=settings.API_KEY

def getRequestBody(body):
    body_unicode = body.decode('utf-8')
    body_data = json.loads(body_unicode)

def assembleUrl(queryParams):
    url=f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}'

# Create your views here.
def get_recipe(request,):
    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)

    print(request.body)
    url=f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return JsonResponse(data)