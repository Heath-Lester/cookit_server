"""View module for handling requests about recipes"""
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
from cookit_api.models import Saved_Recipe, Ingredient, Instruction, Equipment



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

class RecipeSerializer(serializers.ModelSerializer):
    """JSON serializer for Saved Recipes"""
    ingredients = IngredientSerializer(many=True)
    instructions = InstructionSerializer(many=True)
    equipment = EquipmentSerializer(many=True)

    class Meta:
        model = Saved_Recipe
        fields = ('id','spoonacular_id', 'title', 'image', 'source_name',
                  'source_url', 'servings', 'ready_in_minutes', 'summary',
                  'favorite', 'edited', 'ingredients', 'instructions', 'equipment')
        depth = 1


class Saved_Recipes(ViewSet):
    """Request handlers for saved, new, or edited recipes from the Spoonacular API"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        Handles POST request for a new recipe.
        """
        user = User.objects.get(pk=request.auth.user.id)

        new_recipe = Saved_Recipe()
        new_recipe.spoonacular_id = request.data["spoonacularId"]
        new_recipe.user = user
        new_recipe.title = request.data["title"]
        new_recipe.image = request.data["image"]
        new_recipe.source_name = request.data["sourceName"]
        new_recipe.source_url = request.data["sourceUrl"]
        new_recipe.servings = request.data["servings"]
        new_recipe.ready_in_minutes = request.data["readyInMinutes"]
        new_recipe.summary = request.data["summary"]
        new_recipe.favorite = False
        new_recipe.edited = False
        new_recipe.save()

        new_ingredients = request.data["ingredients"]

        i=0

        for new_ingredient in new_ingredients:
            new_ingredient = Ingredient()
            new_ingredient.spoonacular_id = new_recipe.spoonacular_id
            new_ingredient.saved_recipe = Saved_Recipe.objects.get(pk=new_recipe.id)
            new_ingredient.user = user
            new_ingredient.spoon_ingredient_id = request.data["ingredients"][i]["spoonIngredientId"]
            new_ingredient.amount = request.data["ingredients"][i]["amount"]
            new_ingredient.unit = request.data["ingredients"][i]["unit"]
            new_ingredient.name = request.data["ingredients"][i]["name"]
            new_ingredient.aisle = request.data["ingredients"][i]["aisle"]
            new_ingredient.aquired = False
            new_ingredient.save()
            i += 1


        new_instructions = request.data["instructions"]

        i=0

        for new_instruction in new_instructions:
            new_instruction = Instruction()
            new_instruction.spoonacular_id = new_recipe.spoonacular_id
            new_instruction.saved_recipe = Saved_Recipe.objects.get(pk=new_recipe.id)
            new_instruction.user = user
            new_instruction.step_number = request.data["instructions"][i]["number"]
            new_instruction.instruction = request.data["instructions"][i]["step"]
            new_instruction.save()
            i += 1


        new_eqiupment = request.data["equipment"]

        i=0

        for new_item in new_eqiupment:
            new_item = Equipment()
            new_item.spoonacular_id = new_recipe.spoonacular_id
            new_item.saved_recipe = Saved_Recipe.objects.get(pk=new_recipe.id)
            new_item.user = user
            new_item.name = request.data["equipment"][i]["name"]
            new_item.save()
            i += 1

        new_recipe.ingredients = Ingredient.objects.filter(saved_recipe=new_recipe.id)
        new_recipe.instructions = Instruction.objects.filter(saved_recipe=new_recipe.id)
        new_recipe.equipment = Equipment.objects.filter(saved_recipe=new_recipe.id)

        serializer = RecipeSerializer(
            new_recipe, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        Handles GET requests for a single recipe
        """
        try:
            recipe = Saved_Recipe.objects.get(pk=pk)

            recipe.ingredients = Ingredient.objects.filter(saved_recipe=recipe.id)
            recipe.instructions = Instruction.objects.filter(saved_recipe=recipe.id)
            recipe.equipment = Equipment.objects.filter(saved_recipe=recipe.id)

            serializer = RecipeSerializer(recipe, context={'request': request})

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Saved_Recipe.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def update(self, request, pk=None):
    #     """
       
    #     """
    #     product = Product.objects.get(pk=pk)
    #     product.name = request.data["name"]
    #     product.price = request.data["price"]
    #     product.description = request.data["description"]
    #     product.quantity = request.data["quantity"]
    #     product.created_date = request.data["created_date"]
    #     product.location = request.data["location"]

    #     customer = Customer.objects.get(user=request.auth.user)
    #     product.customer = customer

    #     product_category = ProductCategory.objects.get(pk=request.data["category_id"])
    #     product.category = product_category
    #     product.save()

    #     return Response({}, status=status.HTTP_204_NO_CONTENT)

    # def destroy(self, request, pk=None):
    #     """
       
    #     """
    #     try:
    #         product = Product.objects.get(pk=pk)
    #         product.delete()

    #         return Response({}, status=status.HTTP_204_NO_CONTENT)

    #     except Product.DoesNotExist as ex:
    #         return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    #     except Exception as ex:
    #         return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """
        Handles GET requests for all recipes.
        
        """
        user = User.objects.get(pk=request.auth.user.id)

        user_recipes = Saved_Recipe.objects.filter(user=user)

        for recipe in user_recipes:

            recipe.ingredients = Ingredient.objects.filter(saved_recipe=recipe.id)
            recipe.instructions = Instruction.objects.filter(saved_recipe=recipe.id)
            recipe.equipment = Equipment.objects.filter(saved_recipe=recipe.id)

        serializer = RecipeSerializer(
            user_recipes, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def favorites(self, request):
        """Handles GET requests for Favorite recipes"""

        if request.method == "GET":

            user = User.objects.get(pk=request.auth.user.id)

            user_recipes = Saved_Recipe.objects.filter(user=user)

            try:
                favorite_recipes = user_recipes.filter(favorite=True)

                for recipe in favorite_recipes:

                    recipe.ingredients = Ingredient.objects.filter(saved_recipe=recipe.id)
                    recipe.instructions = Instruction.objects.filter(saved_recipe=recipe.id)
                    recipe.equipment = Equipment.objects.filter(saved_recipe=recipe.id)

                serializer = RecipeSerializer(
                    favorite_recipes, many=True, context={'request': request})

                return Response(serializer.data, status=status.HTTP_200_OK)

            except user_recipes.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['patch'], detail=False)
    def favorite(self, request, pk=None):
        """Handles PATCH requests to Favorite recipes"""

        if request.method == "PATCH":

            try:

                recipe = Saved_Recipe.objects.get(pk=pk)

                if recipe.favorite is False:

                    recipe.favorite = True

                elif recipe.favorite is True:

                    recipe.favorite = False

                recipe.ingredients = Ingredient.objects.filter(saved_recipe=recipe.id)
                recipe.instructions = Instruction.objects.filter(saved_recipe=recipe.id)
                recipe.equipment = Equipment.objects.filter(saved_recipe=recipe.id)

                serializer = RecipeSerializer(
                    recipe, many=False, context={'request': request})

                return Response(serializer.data, status=status.HTTP_200_OK)

            except Saved_Recipe.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)