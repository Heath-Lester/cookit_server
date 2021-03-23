# Generated by Django 3.1.7 on 2021-03-23 18:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Saved_Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spoonacular_id', models.IntegerField(null=True)),
                ('title', models.CharField(max_length=100)),
                ('image', models.URLField()),
                ('source_name', models.CharField(max_length=100, null=True)),
                ('source_url', models.URLField(null=True)),
                ('servings', models.IntegerField(null=True)),
                ('ready_in_minutes', models.IntegerField(null=True)),
                ('summary', models.CharField(max_length=5000, null=True)),
                ('favorite', models.BooleanField()),
                ('edited', models.BooleanField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'saved_recipe',
                'verbose_name_plural': 'saved_recipes',
            },
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spoonacular_id', models.IntegerField(null=True)),
                ('saved_recipe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cookit_api.saved_recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'meal',
                'verbose_name_plural': 'meals',
            },
        ),
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spoonacular_id', models.IntegerField(null=True)),
                ('step_number', models.IntegerField()),
                ('instruction', models.CharField(max_length=100, null=True)),
                ('saved_recipe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cookit_api.saved_recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'instruction',
                'verbose_name_plural': 'instructions',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spoonacular_id', models.IntegerField(null=True)),
                ('spoon_ingredient_id', models.IntegerField(null=True)),
                ('amount', models.FloatField()),
                ('unit', models.CharField(max_length=100, null=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('original', models.CharField(max_length=100, null=True)),
                ('aisle', models.CharField(max_length=100, null=True)),
                ('aquired', models.BooleanField()),
                ('saved_recipe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cookit_api.saved_recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ingredient',
                'verbose_name_plural': 'ingredients',
            },
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spoonacular_id', models.IntegerField(null=True)),
                ('name', models.CharField(max_length=50)),
                ('saved_recipe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cookit_api.saved_recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
