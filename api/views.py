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

    url=f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&instructionsRequired=true'

    if("number" in body_data):
        url = url + f'&number={body_data["number"]}'
    else:
        url = url + '&number=10'

    for key in body_data:
        if(key != "number"):
            url = url + f'&{key}={body_data[key]}'

    return url

# %$%$%$%$%$%$% Views %$%$%$%$%$%$%

def get_recipe(request):

    #Parse Body
    body_data = parseBody(request)
    url = constructQueryUrl(body_data)

    #Search for Recipes that Match the Query Parameters
    response = requests.get(url)
    data = response.json()
    return JsonResponse(data)