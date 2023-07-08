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

def constructComplexQueryUrl(body_data):

    url=f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&instructionsRequired=true'

    if("number" in body_data):
        url = url + f'&number={body_data["number"]}'
    else:
        url = url + '&number=10'

    for key in body_data:
        if(key != "number"):
            url = url + f'&{key}={body_data[key]}'

    return url

def grabIds(complexSearchResults):
    ids = ''

    for i in complexSearchResults['results']:
        ids = ids + f"{i['id']},"

    return ids

def constructRecipeInfoQueryUrl(complexSearchResults):
    ids = grabIds(complexSearchResults)
    url=f'https://api.spoonacular.com/recipes/informationBulk?apiKey={API_KEY}&ids={ids}'

    return url


#   ------- Helper Function to formatResponse Below -------
def formatIngredients(extendedIngredients):

    allIngredients = {}

    for ingredient in extendedIngredients:

        formattedIngredient = {
            "original": ingredient.original,
            "amount": ingredient.amount,
            "unit": ingredient.unit
        }

        allIngredients[ingredient.name] = formattedIngredient

    return allIngredients


def formatInstructions(analyzedInstructions):
    pass

#   ------- Format's the Response Object -------
def formatReponse(recipeInfoBulkResults):
    response = {}

    for recipe in recipeInfoBulkResults:

        recipeData = {
            **recipe,
            "ingredients": formatIngredients(recipe.extendedIngredients),
            "instructionSummary": recipe.instructions,
            "instructionSteps": formatInstructions(recipe.analyzedInstructions)
        }

        removeKeys = [
            "vegetarian",
            "vegan",
            "glutenFree",
            "lowFodmap",
            "weightWatcherSmartPoints",
            "gaps",
            "imageType",
            "instructions",
            "analyzedInstructions",
            "report",
            "suspiciousDataScore",
            "approved",
            "unknownIngredients",
            "userTags",
            "originalId",
            "winePairing",
            "occasions"
        ]

        for key in removeKeys:
            recipeData.pop(key, None)


        response[recipe.title] = recipeData

    return response

# %$%$%$%$%$%$% Views %$%$%$%$%$%$%

def get_recipe(request):

    #Parse Body
    body_data = parseBody(request)
    url = constructComplexQueryUrl(body_data)

    #Search for Recipes using Spoonacular Complex Search Route
    complexSearch = requests.get(url)
    complexSearchResults = complexSearch.json()

    #If there are no matching Recipes - Return custom response.
    if (len(complexSearchResults["results"]) == 0):
        return HttpResponse("No matching recipes.")

    #Search for Recipe Info using Spoonacular Recipe Information Bulk Route
    url = constructRecipeInfoQueryUrl(complexSearchResults)
    recipeInfoBulk = requests.get(url)
    recipeInfoBulkResults = recipeInfoBulk.json()

    response = formatReponse(recipeInfoBulkResults)

    return JsonResponse(response, safe=False)