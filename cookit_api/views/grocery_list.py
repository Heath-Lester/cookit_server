import base64
from rest_framework import status
from rest_framework import serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import HttpResponseServerError
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from cookit_api.models import Saved_Recipe, Ingredient, Instruction, Equipment, Meal


class IngredientSerializer(serializers.ModelSerializer):
    """JSON serializer for Ingredients"""
    class Meta:
        model = Ingredient
        fields = ('id', 'spoonacular_id', 'saved_recipe', 'spoon_ingredient_id', 'amount',
                  'unit', 'name', 'aisle', 'aquired')


class Grocery_List(ViewSet):
    """Request handlers for saved, new, or edited recipes added to the meals-to-prep queue."""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        """
        Handles GET requests for all of a users meals.
        
        """

        meals = Meal.objects.filter(user=request.auth.user)

        grocery_list = []

        for meal in meals:

            if meal.saved_recipe is None:

                recipe_ingredients = Ingredient.objects.filter(spoonacular_id=meal.spoonacular_id)

                for ingredient in recipe_ingredients:
                    grocery_list.append(ingredient)

            elif meal.saved_recipe is not None:

                recipe_ingredients = Ingredient.objects.filter(saved_recipe=meal.saved_recipe)

                for ingredient in recipe_ingredients:
                    grocery_list.append(ingredient)

        serializer = IngredientSerializer(
            grocery_list, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
