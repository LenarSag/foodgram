# Generated by Django 3.2.16 on 2024-07-02 14:51

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0008_auto_20240702_1723'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='cart',
            name='unique_recipe_in_cart',
        ),
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_favorite_recipe',
        ),
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('recipe', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together={('recipe', 'user')},
        ),
    ]
