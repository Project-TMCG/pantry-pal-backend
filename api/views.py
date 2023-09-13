from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import requests
import json

# %$%$%$%$%$%$% Environ Variable %$%$%$%$%$%$%

API_KEY=settings.API_KEY

# %$%$%$%$%$%$% Helper Functions %$%$%$%$%$%$%

#   ------- Grabs Query Params from the Request Body -------
def parseBody(request):

    bodyUnicode = request.body.decode('utf-8')
    bodyData = json.loads(bodyUnicode)
    return bodyData

#   ------- Check Query Params from Request Body -------
def checkBodyParams(bodyData):

    invalidParams = []

    validParams = {
        "number": None,
        "cuisine": None,
        "excludeCuisine": None,
        "diet": None,
        "intolerances": None,
        "equipment": None,
        "includeIngredients": None,
        "excludeIngredients": None,
        "type": None,
        "fillIngredients": None,
        "addRecipeInformation": None,
        "addRecipeNutrition": None,
        "author": None,
        "tags": None,
        "recipeBoxId": None,
        "titleMatch": None,
        "maxReadyTime": None,
        "ignorePantry": None,
        "sort": None,
        "sortDirection": None,
        "minCarbs": None,
        "maxCarbs": None,
        "minProtein": None,
        "maxProtein": None,
        "minCalories": None,
        "maxCalories": None,
        "minFat": None,
        "maxFat": None,
        "minAlchohol": None,
        "maxAlchohol": None,
        "minCaffeine": None,
        "maxCaffeine": None,
        "minCholesterol": None,
        "maxCholesterol": None,
        "minFiber": None,
        "maxFiber": None,
        "minSugar": None,
        "maxSugar": None,
        "offset": None,
    }

    for param in bodyData:
        if (param not in validParams):
            invalidParams.append(param)
    
    return invalidParams

#   ------- Constructs Query Url for the Complex Search Endpoint -------
def constructComplexQueryUrl(bodyData):

    url=f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&instructionsRequired=true'

    if ("number" in bodyData):
        url = url + f'&number={bodyData["number"]}'
    else:
        url = url + '&number=10'

    for key in bodyData:
        if(key != "number"):
            url = url + f'&{key}={bodyData[key]}'

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
    url=f'https://api.spoonacular.com/recipes/informationBulk?apiKey={API_KEY}&ids={ids}&includeNutrition=true'

    return url

#   ------- Helper Function to formatResponse Below -------
def formatIngredients(extendedIngredients):

    allIngredients = {}

    for ingredient in extendedIngredients:

        formattedIngredient = {
            "original": ingredient["original"],
            "amount": ingredient["amount"],
            "unit": ingredient["unit"],
            "image": ingredient["image"]
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

#   ------- Helper Function to formatNutrition Below -------
def formatNutrition(nutritionArray):
    nutritionObject = {}
    checkArray = ["Calories", "Fat", "Saturated Fat", "Carbohydrates", "Sugar", "Cholesterol", "Sodium", "Protein", "Fiber"]

    for nutrient in nutritionArray:

        if nutrient["name"] in checkArray:
            formattedNutrient = {
                "amount": nutrient["amount"],
                "unit": nutrient["unit"]
            }

            nutritionObject[nutrient["name"]] = formattedNutrient

    print (nutritionObject)
    return nutritionObject


#   ------- Format's the Response Object -------
def formatReponse(recipeInfoBulkResults):

    response = {}

    for recipe in recipeInfoBulkResults:

        recipeData = {
            **recipe,
            "ingredients": formatIngredients(recipe["extendedIngredients"]),
            "instructionSummary": recipe["instructions"],
            "instructionSteps": formatInstructions(recipe["analyzedInstructions"][0]["steps"]),
            "nutrition": formatNutrition(recipe["nutrition"]["nutrients"])
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
@csrf_exempt
def fetchRecipes(request):

    print(request.method)

    #Parse Body
    bodyData = parseBody(request)

    #Check Query Params from Request Body
    invalidParams = checkBodyParams(bodyData)
    if (len(invalidParams) != 0):
        message = f"Invalid params in request body. Invalid params include: {invalidParams}."
        return HttpResponseBadRequest(message)   

    #Query the Complex Search Endpoint
    url = constructComplexQueryUrl(bodyData)
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