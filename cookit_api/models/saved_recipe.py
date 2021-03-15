from django.db import models
from django.contrib.auth.models import User


class Saved_Recipe(models.Model):

    spoonacular_id = models.IntegerField(null=True, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField()
    image = models.URLField()
    source_name = models.models.CharField(null=True)
    soruce_url = models.URLField(null=True)
    servings = models.IntegerField(null=True)
    ready_in_minutes = models.IntegerField(null=True)
    summary = models.CharField(null=True)
    favorite = models.BooleanField()
    edited = models.BooleanField()
    
    @property
    def ingredients(self):
        return self.__ingredients

    @ingredients.setter
    def ingredients(self, value):
        self.__ingredients = value

    @property
    def cook_ware(self):
        return self.__cook_ware

    @cook_ware.setter
    def cook_ware(self, value):
        self.__cook_ware = value

    @property
    def intructions(self):
        return self.__intructions

    @intructions.setter
    def intructions(self, value):
        self.__intructions = value

    class Meta:
        verbose_name = ("saved_recipe")
        verbose_name_plural = ("saved_recipes")