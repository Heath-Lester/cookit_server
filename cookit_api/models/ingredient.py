from django.db import models
from .saved_recipe import Saved_Recipe
from django.contrib.auth.models import User


class Ingredient(models.Model):

    spoonacular_id = models.IntegerField(null=True)
    saved_recipe = models.ForeignKey(Saved_Recipe, null=True, on_delete=models.CASCADE,)
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    spoon_ingredient_id = models.IntegerField(null=True)
    amount = models.IntegerField()
    unit = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100, null=True)
    aquired = models.BooleanField()

    class Meta:
        verbose_name = ("ingredient")
        verbose_name_plural = ("ingredients")