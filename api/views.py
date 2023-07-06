from django.conf import settings
from django.http import JsonResponse, HttpResponse
import requests
import json


# %$%$%$%$%$%$% Environ Variable %$%$%$%$%$%$%

API_KEY = ''

if settings.DEBUG:
    API_KEY=settings.API_KEY

# %$%$%$%$%$%$% Helper Functions %$%$%$%$%$%$%

def parseBody(request):
    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)
    return body_data

def constructQueryUrl(body_data):
    url=f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}'

    if (body_data["ingredients"]):
        i_list = ','.join(body_data["ingredients"])
        url = url + f'&includeIngredients={i_list}'

    return url

# %$%$%$%$%$%$% Views %$%$%$%$%$%$%
# Create your views here.
def get_recipe(request):
    body_data = parseBody(request)
    url = constructQueryUrl(body_data)

    # return HttpResponse("Testing route without accessing Spoonacular API")
    print(url)
    response = requests.get(url)
    data = response.json()
    return JsonResponse(data)