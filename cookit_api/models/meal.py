from django.db import models
from .saved_recipe import Saved_Recipe
from django.contrib.auth.models import User


class Meal(models.Model):

    spoonacular_id = models.IntegerField(null=True)
    saved_recipe = models.ForeignKey(Saved_Recipe, null=True, on_delete=models.CASCADE,)
    user = models.ForeignKey(User, on_delete=models.CASCADE,)

    class Meta:
        verbose_name = ("meal")
        verbose_name_plural = ("meals")