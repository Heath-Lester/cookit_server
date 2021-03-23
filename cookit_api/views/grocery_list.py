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
from cookit_api.models import Saved_Recipe, Ingredient, Meal


class ConciseRecipeSerializer(serializers.ModelSerializer):
    """JSON serializer for Saved Recipes"""
    class Meta:
        model = Saved_Recipe
        fields = ('id','spoonacular_id', 'title', 'image', 'source_name',
                  'source_url', 'servings', 'ready_in_minutes', 'summary',
                  'favorite', 'edited')

class IngredientSerializer(serializers.ModelSerializer):
    """JSON serializer for Ingredients"""
    saved_recipe = ConciseRecipeSerializer(many=False)
    class Meta:
        model = Ingredient
        fields = ('id', 'spoonacular_id', 'saved_recipe', 'spoon_ingredient_id', 'amount',
                  'unit', 'name', 'original', 'aisle', 'aquired')
    depth = 1

class Grocery_List(ViewSet):
    """Request handlers ingredients from recipes listed in the meals queue."""
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


    @action(methods=['get'], detail=True)
    def aquired(self, request, pk=None):
        """Handles GET requests to aquired or unfavorite a recipe"""

        if request.method == "GET":

            try:
                ingredient = Ingredient.objects.get(pk=pk)

                if ingredient.aquired is False:
                    ingredient.aquired = True
                    ingredient.save(force_update=True)

                    return Response({'message': 'ingredient has been aquired!'}, status=status.HTTP_204_NO_CONTENT)

                elif ingredient.aquired is True:
                    ingredient.aquired = False
                    ingredient.save(force_update=True)

                    return Response({'message': 'ingredient status has been reset.'}, status=status.HTTP_204_NO_CONTENT)

            except Ingredient.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)