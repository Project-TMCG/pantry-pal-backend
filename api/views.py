from django.conf import settings
from django.http import JsonResponse, HttpResponse
import requests
import json

# %$%$%$%$%$%$% Environ Variable %$%$%$%$%$%$%

API_KEY = ''

if settings.DEBUG:
    API_KEY=settings.API_KEY

# %$%$%$%$%$%$% Helper Functions %$%$%$%$%$%$%

#   ------- Grabs Query Params from the Request Body -------
def parseBody(request):

    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)
    return body_data

#   ------- Constructs Query Url for the Complex Search Endpoint -------
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

#   ------- Grabs the Recipe Ids from the result of the Complex Search Endpoint -------
def grabIds(complexSearchResults):
    ids = ''

    for i in complexSearchResults['results']:
        ids = ids + f"{i['id']},"

    return ids


#   ------- Constructs Query Url for the Recipe Info Bulk Endpoint -------
def constructRecipeInfoQueryUrl(complexSearchResults):
    ids = grabIds(complexSearchResults)
    url=f'https://api.spoonacular.com/recipes/informationBulk?apiKey={API_KEY}&ids={ids}'

    return url

#   ------- Helper Function to formatResponse Below -------
def formatIngredients(extendedIngredients):

    allIngredients = {}

    for ingredient in extendedIngredients:

        formattedIngredient = {
            "original": ingredient["original"],
            "amount": ingredient["amount"],
            "unit": ingredient["unit"]
        }

        allIngredients[ingredient["name"]] = formattedIngredient

    return allIngredients

#   ------- Helper Function to formatResponse Below -------
def formatInstructions(allSteps):
    instructionSteps = {}
    
    def extractNames(container):
        allNames = []

        for item in container:
            allNames.append(item["name"])

        return allNames

    for step in allSteps:

        formattedStep = {
            **step,
            "ingredients": extractNames(step["ingredients"]),
            "equipment": extractNames(step["equipment"])
        }

        instructionSteps[step["number"]] = formattedStep

    return instructionSteps

#   ------- Format's the Response Object -------
def formatReponse(recipeInfoBulkResults):

    response = {}

    for recipe in recipeInfoBulkResults:

        recipeData = {
            **recipe,
            "ingredients": formatIngredients(recipe["extendedIngredients"]),
            "instructionSummary": recipe["instructions"],
            "instructionSteps": formatInstructions(recipe["analyzedInstructions"][0]["steps"])
        }

        removeKeys = [
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
            "occasions",
            "extendedIngredients",
            "openLicense",
            "spoonacularSourceUrl",
        ]

        for key in removeKeys:
            recipeData.pop(key, None)


        response[recipe["title"]] = recipeData

    return response

# %$%$%$%$%$%$% Views %$%$%$%$%$%$%

def get_recipe(request):

    #Parse Body
    body_data = parseBody(request)
    url = constructComplexQueryUrl(body_data)

    #Query the Complex Search Endpoint
    complexSearch = requests.get(url)
    complexSearchResults = complexSearch.json()

    #If there are no matching Recipes - Return custom response.
    if (len(complexSearchResults["results"]) == 0):
        return HttpResponse("No matching recipes.")

    #Query the Recipe Info Bulk Endpoint
    url = constructRecipeInfoQueryUrl(complexSearchResults)
    recipeInfoBulk = requests.get(url)
    recipeInfoBulkResults = recipeInfoBulk.json()

    #Format the Result of the Recipe Info Bulk Endpoint
    response = formatReponse(recipeInfoBulkResults)

    #Return Formatted Response Object
    return JsonResponse(response, safe=False)