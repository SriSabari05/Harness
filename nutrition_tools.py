# ──────────────────────────────────────────────────────────────
# nutrition_tools.py — Agent Tools
# ──────────────────────────────────────────────────────────────
# These are the "tools" the AI agent can call.
#
# IMPORTANT DESIGN RULE:
#   The LLM decides WHICH tool to use and extracts parameters.
#   The TOOLS do the actual math / data work.
#   This way, nutrition numbers come from real data — not LLM guesses.
# ──────────────────────────────────────────────────────────────

from food_database import lookup_food, list_all_foods


def tool_food_lookup(food_name: str, quantity_g: float = 100.0) -> dict:
    """
    TOOL 1: Look up nutrition for a food item and scale to quantity.

    How it works:
        1. Search the local food database for the food.
        2. If found, calculate nutrition proportionally:
           value = (database_value_per_100g / 100) × quantity_g
        3. Return structured results.

    Args:
        food_name: What the user wants to look up (e.g., "rice").
        quantity_g: How many grams (default 100g).

    Returns:
        A dict with either the calculated nutrition or an error message.
    """
    # Validate quantity
    if quantity_g <= 0:
        return {"error": "Quantity must be greater than 0 grams."}

    # Search the database
    food = lookup_food(food_name)

    if food is None:
        available = ", ".join(list_all_foods())
        return {
            "error": f"'{food_name}' not found in the database.",
            "available_foods": available,
        }

    # Calculate nutrition proportionally
    # Formula:  actual = (per_100g_value / 100) × user_quantity
    scale = quantity_g / 100.0

    return {
        "food": food["name"],
        "quantity_g": quantity_g,
        "serving_note": food["serving_note"],
        "calories": round(food["calories"] * scale, 1),
        "protein_g": round(food["protein_g"] * scale, 1),
        "carbs_g": round(food["carbs_g"] * scale, 1),
        "fat_g": round(food["fat_g"] * scale, 1),
        "fiber_g": round(food["fiber_g"] * scale, 1),
    }


def tool_meal_suggestion(ingredients: list[str]) -> dict:
    """
    TOOL 2: Check which user ingredients exist in the database.

    This tool does the DATA part — checking which ingredients we have
    nutrition info for. The LLM does the CREATIVE part — suggesting
    the actual meal, recipe, and reasoning.

    Args:
        ingredients: List of ingredient names from the user.

    Returns:
        A dict with found/missing ingredients and their nutrition data.
    """
    found = []
    missing = []

    for item in ingredients:
        food = lookup_food(item.strip())
        if food:
            found.append(food)
        else:
            missing.append(item.strip())

    return {
        "found_ingredients": found,
        "missing_ingredients": missing,
        "available_foods": list_all_foods(),
    }
