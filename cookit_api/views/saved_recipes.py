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
        fields = ('id', 'sooonacular_id', 'saved_recipe', 'user', 'spoon_ingredient_id', 'amount',
                  'unit', 'name', 'aisle', 'aquired')

class InstructionSerializer(serializers.ModelSerializer):
    """JSON serializer for Instructions"""
    class Meta:
        model = Ingredient
        fields = ('id', 'sooonacular_id', 'saved_recipe', 'user', 'step_number', 'instruction')

class EquipmentSerializer(serializers.ModelSerializer):
    """JSON serializer for Equipment"""
    class Meta:
        model = Equipment
        fields = ('id', 'sooonacular_id', 'saved_recipe', 'user', 'name')

class RecipeSerializer(serializers.ModelSerializer):
    """JSON serializer for Saved Recipes"""
    ingredients = IngredientSerializer(many=True)
    instructions = InstructionSerializer(many=True)
    equipment = EquipmentSerializer(many=True)

    class Meta:
        model = Saved_Recipe
        fields = ('id','spoonacular_id', 'user', 'title', 'image', 'source_name',
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


        serializer = RecipeSerializer(
            new_recipe, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def retrieve(self, request, pk=None):
    #     """
        
    #     """
    #     try:
    #         product = Product.objects.get(pk=pk)
    #         serializer = ProductSerializer(product, context={'request': request})
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     except Product.DoesNotExist as ex:
    #         return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    #     except Exception as ex:
    #         return HttpResponseServerError(ex, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    # def list(self, request):
    #     """
        
    #     """
    #     products = Product.objects.all()

    #     # Support filtering by category and/or quantity
    #     category = self.request.query_params.get('category', None)
    #     quantity = self.request.query_params.get('quantity', None)
    #     order = self.request.query_params.get('order_by', None)
    #     direction = self.request.query_params.get('direction', None)
    #     number_sold = self.request.query_params.get('number_sold', None)

    #     if order is not None:
    #         order_filter = order

    #         if direction is not None:
    #             if direction == "desc":
    #                 order_filter = f'-{order}'

    #         products = products.order_by(order_filter)

    #     if category is not None:
    #         products = products.filter(category__id=category)

    #     if quantity is not None:
    #         products = products.order_by("-created_date")[:int(quantity)]

    #     if number_sold is not None:
    #         def sold_filter(product):
    #             if product.number_sold <= int(number_sold):
    #                 return True
    #             return False

    #         products = filter(sold_filter, products)

    #     serializer = ProductSerializer(
    #         products, many=True, context={'request': request})
    #     return Response(serializer.data)

    # @action(methods=['post'], detail=True)
    # def recommend(self, request, pk=None):
    #     """Recommend products to other users"""

    #     if request.method == "POST":
    #         rec = Recommendation()
    #         rec.recommender = Customer.objects.get(user=request.auth.user)
    #         rec.customer = Customer.objects.get(user__id=request.data["recipient"])
    #         rec.product = Product.objects.get(pk=pk)

    #         rec.save()

    #         return Response(None, status=status.HTTP_204_NO_CONTENT)

    #     return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # @action(methods=['post', 'delete'], detail=True)
    # def like(self, request, pk=None):
    #     """Managing users liking products"""

    #     if request.method == "POST":
    #         product = Product.objects.get(pk=pk)

    #         customer = Customer.objects.get(user=request.auth.user)

    #         try:
    #             like = Like.objects.get(
    #                 product=product, customer=customer)
    #             return Response(
    #                 {'message': 'Customer already liked up this product.'},
    #                 status=status.HTTP_422_UNPROCESSABLE_ENTITY
    #             )
    #         except Like.DoesNotExist:
    #             like = Like()
    #             like.product = product
    #             like.customer = customer
    #             like.save()

    #             return Response({}, status=status.HTTP_201_CREATED)

    #     elif request.method == "DELETE":
    #         try:
    #             product = Product.objects.get(pk=pk)
    #         except Product.DoesNotExist:
    #             return Response(
    #                 {'message': 'The product does not exist.'},
    #                 status=status.HTTP_404_NOT_FOUND
    #             )

    #         customer = Customer.objects.get(user=request.auth.user)

    #         try:
    #             like = Like.objects.get(
    #                 product=product, customer=customer)
    #             like.delete()
    #             return Response(None, status=status.HTTP_204_NO_CONTENT)

    #         except Like.DoesNotExist:
    #             return Response(
    #                 {'message': 'The current user has not liked this product.'},
    #                 status=status.HTTP_404_NOT_FOUND
    #             )

    #     return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # @action(methods=['get'], detail=False)
    # def liked(self, request):
    #     """Listing all of a users liked products"""

    #     if request.method == "GET":

    #         customer = Customer.objects.get(user=request.auth.user)

    #         liked_products = []

    #         try:
    #             likes= Like.objects.filter(
    #                 customer=customer
    #             )

    #             for like in likes:

    #                 product = Product.objects.get(pk=like.product_id)
    #                 liked_products.append(product)

    #             serializer = ProductSerializer(liked_products, many=True, context={'request': request})

    #             return Response(serializer.data, status=status.HTTP_200_OK)

    #         except Like.DoesNotExist:
    #             return Response({'message': 'Customer has not liked any products.'}, 
    #                 status=status.HTTP_404_NOT_FOUND)

        

        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)