# ──────────────────────────────────────────────────────────────
# food_database.py — Local Food Nutrition Database
# ──────────────────────────────────────────────────────────────
# This module stores nutrition data for common foods.
# All values are per 100 grams of the food item.
#
# WHY a local database?
#   The LLM can hallucinate nutrition numbers. By keeping a
#   real data source here, we do math in Python and only use
#   the LLM for reasoning — never for inventing calorie counts.
# ──────────────────────────────────────────────────────────────

# Each food entry:  name → {calories, protein_g, carbs_g, fat_g, fiber_g, serving_note}
# Sources: USDA FoodData Central (approximate values, rounded for simplicity)

FOOD_DB = {
    "rice": {
        "calories": 130,
        "protein_g": 2.7,
        "carbs_g": 28.0,
        "fat_g": 0.3,
        "fiber_g": 0.4,
        "serving_note": "cooked white rice",
    },
    "chicken breast": {
        "calories": 165,
        "protein_g": 31.0,
        "carbs_g": 0.0,
        "fat_g": 3.6,
        "fiber_g": 0.0,
        "serving_note": "cooked, skinless",
    },
    "egg": {
        "calories": 155,
        "protein_g": 13.0,
        "carbs_g": 1.1,
        "fat_g": 11.0,
        "fiber_g": 0.0,
        "serving_note": "whole, raw (1 large egg ≈ 50g)",
    },
    "banana": {
        "calories": 89,
        "protein_g": 1.1,
        "carbs_g": 23.0,
        "fat_g": 0.3,
        "fiber_g": 2.6,
        "serving_note": "raw (1 medium ≈ 118g)",
    },
    "milk": {
        "calories": 61,
        "protein_g": 3.2,
        "carbs_g": 4.8,
        "fat_g": 3.3,
        "fiber_g": 0.0,
        "serving_note": "whole milk",
    },
    "bread": {
        "calories": 265,
        "protein_g": 9.0,
        "carbs_g": 49.0,
        "fat_g": 3.2,
        "fiber_g": 2.7,
        "serving_note": "white bread (1 slice ≈ 30g)",
    },
    "potato": {
        "calories": 77,
        "protein_g": 2.0,
        "carbs_g": 17.0,
        "fat_g": 0.1,
        "fiber_g": 2.2,
        "serving_note": "boiled, without skin",
    },
    "apple": {
        "calories": 52,
        "protein_g": 0.3,
        "carbs_g": 14.0,
        "fat_g": 0.2,
        "fiber_g": 2.4,
        "serving_note": "raw (1 medium ≈ 182g)",
    },
    "paneer": {
        "calories": 265,
        "protein_g": 18.3,
        "carbs_g": 1.2,
        "fat_g": 20.8,
        "fiber_g": 0.0,
        "serving_note": "Indian cottage cheese",
    },
    "dal": {
        "calories": 116,
        "protein_g": 9.0,
        "carbs_g": 20.0,
        "fat_g": 0.4,
        "fiber_g": 8.0,
        "serving_note": "cooked lentils (toor/masoor)",
    },
    "oats": {
        "calories": 389,
        "protein_g": 16.9,
        "carbs_g": 66.0,
        "fat_g": 6.9,
        "fiber_g": 10.6,
        "serving_note": "dry rolled oats",
    },
    "tomato": {
        "calories": 18,
        "protein_g": 0.9,
        "carbs_g": 3.9,
        "fat_g": 0.2,
        "fiber_g": 1.2,
        "serving_note": "raw",
    },
    "onion": {
        "calories": 40,
        "protein_g": 1.1,
        "carbs_g": 9.3,
        "fat_g": 0.1,
        "fiber_g": 1.7,
        "serving_note": "raw",
    },
    "spinach": {
        "calories": 23,
        "protein_g": 2.9,
        "carbs_g": 3.6,
        "fat_g": 0.4,
        "fiber_g": 2.2,
        "serving_note": "raw",
    },
    "yogurt": {
        "calories": 59,
        "protein_g": 10.0,
        "carbs_g": 3.6,
        "fat_g": 0.4,
        "fiber_g": 0.0,
        "serving_note": "plain, low-fat",
    },
}


def lookup_food(food_name: str) -> dict | None:
    """
    Look up a food item in the local database.

    Args:
        food_name: Name of the food (case-insensitive).

    Returns:
        A dict with nutrition info (per 100g), or None if not found.
    """
    key = food_name.strip().lower()

    # Direct match
    if key in FOOD_DB:
        return {"name": key, **FOOD_DB[key]}

    # Partial match — e.g. "chicken" matches "chicken breast"
    for db_key, data in FOOD_DB.items():
        if key in db_key or db_key in key:
            return {"name": db_key, **data}

    return None


def list_all_foods() -> list[str]:
    """Return a list of all food names in the database."""
    return list(FOOD_DB.keys())
