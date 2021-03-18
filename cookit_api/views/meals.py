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

class InstructionSerializer(serializers.ModelSerializer):
    """JSON serializer for Instructions"""
    class Meta:
        model = Instruction
        fields = ('id', 'spoonacular_id', 'saved_recipe', 'step_number', 'instruction')

class EquipmentSerializer(serializers.ModelSerializer):
    """JSON serializer for Equipment"""
    class Meta:
        model = Equipment
        fields = ('id', 'spoonacular_id', 'saved_recipe', 'name')

class MealSerializer(serializers.ModelSerializer):
    """JSON serializer for a meal to prepare"""
    class Meta:
        model = Meal
        fields = ('id', 'spoonacular_id', 'saved_recipe')


class ConciseRecipeSerializer(serializers.ModelSerializer):
    """JSON serializer for Saved Recipes"""
    class Meta:
        model = Saved_Recipe
        fields = ('id','spoonacular_id', 'title', 'image', 'source_name',
                  'source_url', 'servings', 'ready_in_minutes', 'summary',
                  'favorite', 'edited')

class DetailedMealSerializer(serializers.ModelSerializer):
    """JSON serializer for a meal to prepare"""
    ingredients = IngredientSerializer(many=True)
    instructions = InstructionSerializer(many=True)
    equipment = EquipmentSerializer(many=True)
    saved_recipe = ConciseRecipeSerializer(many=False)
    class Meta:
        model = Meal
        fields = ('id', 'spoonacular_id', 'saved_recipe', 'ingredients', 'instructions', 'equipment')
    depth = 1


class Meals(ViewSet):
    """Request handlers for saved, new, or edited recipes added to the meals-to-prep queue."""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        Handles POST request for a meal to prepare.
        """
        user = User.objects.get(pk=request.auth.user.id)
        spoonacular_id = request.data["spoonacularId"]
        saved_recipe_id = request.data["savedRecipeId"]

        if spoonacular_id is None:
            user_made_recipe = Meal()
            user_made_recipe.saved_recipe = Saved_Recipe.objects.get(pk=saved_recipe_id)
            user_made_recipe.user = user
            user_made_recipe.save()

            serializer = MealSerializer(
                user_made_recipe, context={'request': request})

        elif saved_recipe_id is None:
            non_saved_recipe = Meal()
            non_saved_recipe.spoonacular_id = spoonacular_id
            non_saved_recipe.user = user
            non_saved_recipe.save()

            new_ingredients = request.data["ingredients"]

            i=0

            for ingredient in new_ingredients:
                ingredient = Ingredient()
                ingredient.spoonacular_id = non_saved_recipe.spoonacular_id
                ingredient.user = user
                ingredient.spoon_ingredient_id = request.data["ingredients"][i]["spoonIngredientId"]
                ingredient.amount = request.data["ingredients"][i]["amount"]
                ingredient.unit = request.data["ingredients"][i]["unit"]
                ingredient.name = request.data["ingredients"][i]["name"]
                ingredient.aisle = request.data["ingredients"][i]["aisle"]
                ingredient.aquired = False
                ingredient.save()
                i += 1


            new_instructions = request.data["instructions"]

            i=0

            for instruction in new_instructions:
                instruction = Instruction()
                instruction.spoonacular_id = non_saved_recipe.spoonacular_id
                instruction.user = user
                instruction.step_number = request.data["instructions"][i]["number"]
                instruction.instruction = request.data["instructions"][i]["step"]
                instruction.save()
                i += 1


            new_eqiupment = request.data["equipment"]

            i=0

            for equipment in new_eqiupment:
                equipment = Equipment()
                equipment.spoonacular_id = non_saved_recipe.spoonacular_id
                equipment.user = user
                equipment.name = request.data["equipment"][i]["name"]
                equipment.save()
                i += 1

            non_saved_recipe.ingredients = Ingredient.objects.filter(spoonacular_id=non_saved_recipe.spoonacular_id)
            non_saved_recipe.instructions = Instruction.objects.filter(spoonacular_id=non_saved_recipe.spoonacular_id)
            non_saved_recipe.equipment = Equipment.objects.filter(spoonacular_id=non_saved_recipe.spoonacular_id)

            serializer = DetailedMealSerializer(
                non_saved_recipe, context={'request': request})

        elif spoonacular_id is not None and saved_recipe_id is not None:
            saved_recipe = Meal()
            saved_recipe.spoonacular_id = spoonacular_id
            saved_recipe.saved_recipe = Saved_Recipe.objects.get(pk=saved_recipe_id)
            saved_recipe.user = user
            saved_recipe.save()

            serializer = MealSerializer(
                saved_recipe, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def destroy(self, request, pk=None):
        """
        Handles DELETE requests for all meals.
       
        """
        user = User.objects.get(pk=request.auth.user.id)

        try:
            meal = Meal.objects.get(pk=pk, user=user)

            if meal.saved_recipe is None:

                ingredients = Ingredient.objects.filter(spoonacular_id=meal.spoonacular_id)
                instructions = Instruction.objects.filter(spoonacular_id=meal.spoonacular_id)
                equipment = Equipment.objects.filter(spoonacular_id=meal.spoonacular_id)

                for ingredient in ingredients:
                    ingredient.delete()
                for instruction in instructions:
                    instruction.delete()
                for item in equipment:
                    item.delete()

                meal.delete()

                return Response({}, status=status.HTTP_204_NO_CONTENT)

            if meal.saved_recipe is not None:

                meal.delete()

                return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Meal.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def list(self, request):
        """
        Handles GET requests for all of a users meals.
        
        """

        meals = Meal.objects.filter(user=request.auth.user)

        for meal in meals:

            if meal.saved_recipe is None:

                meal.ingredients = Ingredient.objects.filter(spoonacular_id=meal.spoonacular_id)
                meal.instructions = Instruction.objects.filter(spoonacular_id=meal.spoonacular_id)
                meal.equipment = Equipment.objects.filter(spoonacular_id=meal.spoonacular_id)

            if meal.saved_recipe is not None:

                meal.ingredients = Ingredient.objects.filter(saved_recipe=meal.saved_recipe)
                meal.instructions = Instruction.objects.filter(saved_recipe=meal.saved_recipe)
                meal.equipment = Equipment.objects.filter(saved_recipe=meal.saved_recipe)

        serializer = DetailedMealSerializer(
            meals, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
       
    @action(methods=['delete'], detail=False)
    def complete(self, request):
        """Handles DELETE requests to reset meal-to-prep queue."""

        if request.method == "DELETE":

            all_user_meals = Meal.objects.filter(user=request.auth.user)

            for meal in all_user_meals:

                if meal.saved_recipe is None:
                    ingredients = Ingredient.objects.filter(spoonacular_id=meal.spoonacular_id)
                    instructions = Instruction.objects.filter(spoonacular_id=meal.spoonacular_id)
                    equipment = Equipment.objects.filter(spoonacular_id=meal.spoonacular_id)

                    for ingredient in ingredients:
                        ingredient.delete()
                    for instruction in instructions:
                        instruction.delete()
                    for item in equipment:
                        item.delete()

                meal.delete()

            return Response({'message': 'Meal list has been reset!'}, status=status.HTTP_204_NO_CONTENT)

        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)