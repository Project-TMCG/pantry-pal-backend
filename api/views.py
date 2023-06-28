from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def get_recipe(request, id=None):
    message = f'You have retrieved ID {id}.'
    return HttpResponse(message)