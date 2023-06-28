from .models import Recipe
from rest_framework import serializers

class RecipeSerializer(serializer.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = ('name', 'alias')