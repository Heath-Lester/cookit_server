"""View module for handling requests about recipes"""
import base64
from rest_framework import status
from rest_framework import serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from cookit_api.models import Saved_Recipe, Ingredient, Instruction, Equipment



class IngredientSerializer(serializers.ModelSerializer):
    """JSON serializer for Ingredients"""
    class Meta:
        model = Ingredient
        fields = ('id', 'spoonacular_id', 'saved_recipe', 'spoon_ingredient_id', 'amount',
                  'unit', 'name', 'original', 'aisle', 'aquired')

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
            new_ingredient.spoon_ingredient_id = request.data["ingredients"][i]["id"]
            new_ingredient.amount = request.data["ingredients"][i]["amount"]
            new_ingredient.unit = request.data["ingredients"][i]["measures"]["us"]["unitLong"]
            new_ingredient.name = request.data["ingredients"][i]["name"]
            new_ingredient.original = request.data["ingredients"][i]["original"]
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


    def update(self, request, pk=None):
        """
        Handles PUT requests for all saved recipes.
       
        """
        user = User.objects.get(pk=request.auth.user.id)

        recipe = Saved_Recipe.objects.get(pk=pk)

        old_ingredients = Ingredient.objects.filter(saved_recipe=pk)
        old_instructions = Instruction.objects.filter(saved_recipe=pk)
        old_equipment = Equipment.objects.filter(saved_recipe=pk)

        # Deletes all old Ingredients, Instructions, and Equipment
        for ingredient in old_ingredients:
            ingredient.delete()
        for instruction in old_instructions:
            instruction.delete()
        for equipment in old_equipment:
            equipment.delete()

        recipe.title = request.data["title"]
        recipe.image = request.data["image"]
        recipe.servings = request.data["servings"]
        recipe.ready_in_minutes = request.data["readyInMinutes"]
        recipe.summary = request.data["summary"]
        recipe.edited = True
        recipe.save()

        new_ingredients = request.data["ingredients"]

        i=0

        for ingredient in new_ingredients:
            new_ingredient = Ingredient()
            new_ingredient.saved_recipe = Saved_Recipe.objects.get(pk=recipe.id)
            new_ingredient.user = user
            new_ingredient.amount = float(request.data["ingredients"][i]["amount"])
            new_ingredient.name = request.data["ingredients"][i]["title"]

            # Deconstructs the float 'amount' to create the 'original' ingredient description
            float_to_integer = str(new_ingredient.amount).split('.')
            whole_number = int(float_to_integer[0])
            decimal = int(float_to_integer[1])
            fraction = ""

            # Finds if spoonacular's tablespoon default is present
            string_divider = ""
            unit = request.data["ingredients"][i]["unit"]
            if unit == 'Tbsps' or unit == 'Tbsp':
                new_ingredient.unit = 'tablespoon'

            # Converts plural units to singular units
            elif str(unit).endswith('ves'):
                unit_list = list(unit)
                unit_list.pop(-1)
                unit_list.pop(-1)
                unit_list.pop(-1)
                unit_list.append('f')
                unit_tuple = tuple(unit_list)
                singular_unit = string_divider.join(unit_tuple)
                new_ingredient.unit = str(singular_unit)

            elif str(unit).endswith(tuple(['ches', 'ses', 'shes', 'sses', 'xes', 'zes', ])):
                unit_list = list(unit)
                unit_list.pop(-1)
                unit_list.pop(-1)
                unit_tuple = tuple(unit_list)
                singular_unit = string_divider.join(unit_tuple)
                new_ingredient.unit = str(singular_unit)

            elif str(unit).endswith(tuple(['boes', 'coes', 'does', 'foes', 'goes', 'hoes', 'joes', 'koes', 'loes', 'moes', 'noes', 'poes', 'qoes', 'roes', 'soes', 'toes', 'voes', 'woes', 'xoes', 'zoes', ])):
                unit_list = list(unit)
                unit_list.pop(-1)
                unit_list.pop(-1)
                unit_tuple = tuple(unit_list)
                singular_unit = string_divider.join(unit_tuple)
                new_ingredient.unit = str(singular_unit)

            elif str(unit).endswith('ies'):
                unit_list = list(unit)
                unit_list.pop(-1)
                unit_list.pop(-1)
                unit_list.pop(-1)
                unit_list.append('y')
                unit_tuple = tuple(unit_list)
                singular_unit = string_divider.join(unit_tuple)
                new_ingredient.unit = str(singular_unit)
                
            elif str(unit).endswith('s'):
                unit_list = list(unit)
                unit_list.pop(-1)
                unit_tuple = tuple(unit_list)
                singular_unit = string_divider.join(unit_tuple)
                new_ingredient.unit = str(singular_unit)

            else:
                new_ingredient.unit = request.data["ingredients"][i]["unit"]

            # Converts the decimal into a fraction
            if decimal != 0:
                if decimal == 25:
                    fraction = "1/4"
                elif str(decimal).startswith('3') and str(decimal).endswith('3'):
                    fraction = "1/3"
                elif decimal == 5:
                    fraction = "1/2"
                elif str(decimal).startswith('6') and str(decimal).endswith('6'):
                    fraction = "2/3"
                elif decimal == 75:
                    fraction = "3/4"
            
            # Sentece builder for singular units
            measurements = set(("teaspoon", "tablespoon", "ounce", "cup", "pint", "quart", "gallon", "pound", "gram", "milligram", "inch", "centimeter", "slice", "serving", "piece", "stick", "pinch"))
            if whole_number <= 1:

                if decimal == 0:
                    if new_ingredient.unit == '':
                        new_ingredient.original = str(whole_number) + " " + new_ingredient.name

                    elif new_ingredient.unit not in measurements:
                            new_ingredient.original = str(whole_number) + " " + new_ingredient.unit + " " + new_ingredient.name

                    else:
                        new_ingredient.original = str(whole_number) + " " + new_ingredient.unit + " of " + new_ingredient.name

                else:
                    if new_ingredient.unit == '':
                        new_ingredient.original = fraction + " " + new_ingredient.name

                    elif new_ingredient.unit not in measurements:
                            new_ingredient.original = str(whole_number) + " " + new_ingredient.unit + " " + new_ingredient.name
                    
                    else:
                        new_ingredient.original = fraction + " " + new_ingredient.unit + " of " + new_ingredient.name

            # Sentece builder for plural units 
            elif whole_number > 1:

                if decimal == 0:

                    if new_ingredient.unit == '':
                        new_ingredient.original = str(whole_number) + " " + new_ingredient.name

                    elif new_ingredient.unit not in measurements:
                            new_ingredient.original = str(whole_number) + " " + new_ingredient.unit + " " + new_ingredient.name

                    else:
                        new_ingredient.original = str(whole_number) + " " + new_ingredient.unit + "s of " + new_ingredient.name

                elif decimal > 0:

                    if new_ingredient.unit == '':
                        new_ingredient.original = str(whole_number) + " " + fraction + " " + new_ingredient.name

                    elif new_ingredient.unit not in measurements:
                        new_ingredient.original = str(whole_number) + " " + fraction + " " + new_ingredient.unit + " " + new_ingredient.name

                    elif new_ingredient.unit.endswith(tuple(['ch', 's', 'sh', 'ss', 'x', 'z', ])):
                        new_ingredient.original = str(whole_number) + " " + fraction + " " + new_ingredient.unit + "es of " + new_ingredient.name
                    
                    elif new_ingredient.unit.endswith('f'):
                        unit_list = list(new_ingredient)
                        unit_list.pop(-1)
                        unit_tuple = tuple(unit_list)
                        unit_wo_affix = string_divider.join(unit_tuple)
                        unit_string = str(unit_wo_affix)
                        new_ingredient.original = str(whole_number) + " " + fraction + " " + unit_string + "ves of " + new_ingredient.name

                    elif new_ingredient.unit.endswith('fe'):
                        unit_list = list(new_ingredient)
                        unit_list.pop(-1)
                        unit_list.pop(-1)
                        unit_tuple = tuple(unit_list)
                        unit_wo_affix = string_divider.join(unit_tuple)
                        unit_string = str(unit_wo_affix)
                        new_ingredient.original = str(whole_number) + " " + fraction + " " + unit_string + "ves of " + new_ingredient.name

                    elif new_ingredient.unit.endswith(tuple(['bo', 'co', 'do', 'fo', 'go', 'ho', 'jo', 'ko', 'lo', 'mo', 'no', 'po', 'qo', 'ro', 'so', 'to', 'vo', 'wo', 'xo', 'zo', ])):
                        new_ingredient.original = str(whole_number) + " " + fraction + " " + new_ingredient.unit + "es of " + new_ingredient.name

                    elif new_ingredient.unit.endswith(tuple(['by', 'cy', 'dy', 'fy', 'gy', 'hy', 'jy', 'ky', 'ly', 'my', 'ny', 'py', 'qy', 'ry', 'sy', 'ty', 'vy', 'wy', 'xy', 'zy', ])):
                        unit_list = list(new_ingredient)
                        unit_list.pop(-1)
                        unit_tuple = tuple(unit_list)
                        unit_wo_affix = string_divider.join(unit_tuple)
                        unit_string = str(unit_wo_affix)
                        new_ingredient.original = str(whole_number) + " " + fraction + " " + unit_string + "ies of " + new_ingredient.name
                    
                    else:
                        new_ingredient.original = str(whole_number) + " " + fraction + " " + new_ingredient.unit + "s of " + new_ingredient.name

            new_ingredient.aisle = request.data["ingredients"][i]["aisle"]
            new_ingredient.aquired = False
            new_ingredient.save()
            i += 1


        new_instructions = request.data["instructions"]

        i=0

        for instruction in new_instructions:
            new_instruction = Instruction()
            new_instruction.saved_recipe = Saved_Recipe.objects.get(pk=recipe.id)
            new_instruction.user = user
            new_instruction.step_number = i + 1
            new_instruction.instruction = request.data["instructions"][i]["instruction"]
            new_instruction.save()
            i += 1


        new_eqiupment = request.data["equipment"]

        i=0

        for item in new_eqiupment:
            new_item = Equipment()
            new_item.saved_recipe = Saved_Recipe.objects.get(pk=recipe.id)
            new_item.user = user
            new_item.name = request.data["equipment"][i]["name"]
            new_item.save()
            i += 1


        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        Handles DELETE requests for all saved recipes.
       
        """
        try:
            recipe = Saved_Recipe.objects.get(pk=pk)
            ingredients = Ingredient.objects.filter(saved_recipe=recipe.id)
            instructions = Instruction.objects.filter(saved_recipe=recipe.id)
            equipment = Equipment.objects.filter(saved_recipe=recipe.id)

            for ingredient in ingredients:
                ingredient.delete()
            for instruction in instructions:
                instruction.delete()
            for item in equipment:
                item.delete()

            recipe.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Saved_Recipe.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    def list(self, request):
        """
        Handles GET requests for all saved recipes.
        
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

            user_recipes = Saved_Recipe.objects.filter(user=request.auth.user)

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

    @action(methods=['get'], detail=True)
    def favorite(self, request, pk=None):
        """Handles GET requests to favorite or unfavorite a recipe"""

        if request.method == "GET":

            try:

                recipe = Saved_Recipe.objects.get(pk=pk)

                if recipe.favorite is False:
                    recipe.favorite = True
                    recipe.save(force_update=True)

                    return Response({'message': 'Recipe has been favorited!'}, status=status.HTTP_204_NO_CONTENT)

                elif recipe.favorite is True:
                    recipe.favorite = False
                    recipe.save(force_update=True)

                    return Response({'message': 'Recipe has been unfavorited.'}, status=status.HTTP_204_NO_CONTENT)

            except Saved_Recipe.DoesNotExist as ex:
                return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

            except Exception as ex:
                return HttpResponseServerError(ex, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['post'], detail=False)
    def new(self, request):
        """Handles POST requests for user-made recipes"""

        if request.method == "POST":

            user = User.objects.get(pk=request.auth.user.id)

            new_recipe = Saved_Recipe()
            new_recipe.user = user
            new_recipe.title = request.data["title"]
            new_recipe.image = request.data["image"]
            new_recipe.source_name = user.first_name + " " + user.last_name
            new_recipe.servings = int(request.data["servings"])
            new_recipe.ready_in_minutes = int(request.data["readyInMinutes"])
            new_recipe.summary = request.data["summary"]
            new_recipe.favorite = False
            new_recipe.edited = False
            new_recipe.save()

            new_ingredients = request.data["ingredients"]

            i=0

            for new_ingredient in new_ingredients:
                new_ingredient = Ingredient()
                new_ingredient.saved_recipe = Saved_Recipe.objects.get(pk=new_recipe.id)
                new_ingredient.user = user
                new_ingredient.amount = float(request.data["ingredients"][i]["amount"])
                new_ingredient.unit = request.data["ingredients"][i]["unit"]
                new_ingredient.name = request.data["ingredients"][i]["title"]

                if new_ingredient.unit == "None" and new_ingredient.amount > 1.0:
                    new_ingredient.original = str(new_ingredient.amount) + " " + new_ingredient.name + "s"

                elif new_ingredient.unit == "None" and new_ingredient.amount <= 1.0:
                    new_ingredient.original = str(new_ingredient.amount) + " " + new_ingredient.name

                elif new_ingredient.amount > 1.0:
                    new_ingredient.original = str(new_ingredient.amount) + " " + new_ingredient.unit + "s of " + new_ingredient.name

                elif new_ingredient.amount <= 1.0:
                    new_ingredient.original = str(new_ingredient.amount) + " " + new_ingredient.unit + " of " + new_ingredient.name

                new_ingredient.aisle = request.data["ingredients"][i]["aisle"]
                new_ingredient.aquired = False
                new_ingredient.save()
                i += 1


            new_instructions = request.data["instructions"]

            i=0

            for new_instruction in new_instructions:
                new_instruction = Instruction()
                new_instruction.saved_recipe = Saved_Recipe.objects.get(pk=new_recipe.id)
                new_instruction.user = user
                new_instruction.step_number = i + 1
                new_instruction.instruction = request.data["instructions"][i]["instruction"]
                new_instruction.save()
                i += 1


            new_eqiupment = request.data["equipment"]

            i=0

            for new_item in new_eqiupment:
                new_item = Equipment()
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

        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)