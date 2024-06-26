# flake8: noqa
import json


input_file_path = "ingredients.json"
output_file_path = "ingredients_for_db.json"

tags = [
    {
        "model": "recipes.tag",
        "pk": 1,
        "fields": {
            "name": "завтрак",
            "slug": "breakfast"
        }
    },
    {
        "model": "recipes.tag",
        "pk": 2,
        "fields": {
            "name": "обед",
            "slug": "lunch"
        }
    },
    {
        "model": "recipes.tag",
        "pk": 3,
        "fields": {
            "name": "ужин",
            "slug": "dinner"
        }
    }
]

with open(input_file_path, "r", encoding="utf-8") as input_file:
    ingredients = json.load(input_file)

with open(output_file_path, "w", encoding="utf-8") as output_file:
    processed_ingredients = []
    processed_ingredients.extend(tags)
    for pk, ingredient in enumerate(ingredients, start=1):
        values = {}
        values["model"] = "recipes.ingredient"
        values["pk"] = pk
        values["fields"] = ingredient
        processed_ingredients.append(values)

    json.dump(processed_ingredients, output_file, ensure_ascii=False, indent=4)
