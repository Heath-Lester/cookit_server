from django.db import models
from .saved_recipe import Saved_Recipe
from django.contrib.auth.models import User


class Instruction(models.Model):

    spoonacular_id = models.IntegerField(null=True)
    saved_recipe = models.ForeignKey(Saved_Recipe, null=True, on_delete=models.CASCADE,)
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    step_number = models.IntegerField()
    instruction = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = ("instruction")
        verbose_name_plural = ("instructions")