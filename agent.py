# ──────────────────────────────────────────────────────────────
# agent.py — The AI Agent
# ──────────────────────────────────────────────────────────────
# This is the BRAIN of NutriGuide AI.
#
# What makes this an "agent" and not just a chatbot?
#   A chatbot sends your message to an LLM and returns the response.
#   An AGENT follows a loop:
#     1. Understand what the user wants (intent detection)
#     2. Decide if a tool is needed
#     3. Call the tool and get real data
#     4. Use the LLM + tool results to build the final answer
#
# This is called the "Reason → Act → Observe" pattern.
# ──────────────────────────────────────────────────────────────

import os
import json
from google import genai
from dotenv import load_dotenv
from nutrition_tools import tool_food_lookup, tool_meal_suggestion
from food_database import list_all_foods

# Load API key from .env file
load_dotenv()

# ─── Configure Gemini Client ────────────────────────────────

def get_client():
    """
    Create a Gemini client using the key from .env.
    Returns the client, or None if the key is missing.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        return None
    return genai.Client(api_key=api_key)


# ─── System Prompt ───────────────────────────────────────────
# This tells the LLM who it is and how to behave.

SYSTEM_PROMPT = """You are NutriGuide AI, a helpful nutrition assistant.

RULES YOU MUST FOLLOW:
1. Only answer questions about food, nutrition, diet, and healthy eating.
2. NEVER invent or guess specific nutrition numbers (calories, protein, etc.).
   If the user asks for specific values, say you'll look it up using your tools.
3. NEVER diagnose medical conditions or recommend medications.
4. NEVER recommend extreme diets, starvation, or unsafe weight loss.
5. For medical diet needs, recommend consulting a healthcare professional.
6. Keep answers practical, friendly, and evidence-based.
7. If you don't know something, say so honestly.
8. Mark any estimates clearly as "approximate" or "estimated".
"""


# ─── Step 1: Detect Intent ──────────────────────────────────
# We ask the LLM to classify what the user wants.

INTENT_PROMPT = """Analyze the user's latest message in light of the recent conversation history to determine their intent.

Recent conversation:
{history_text}

User message: "{user_message}"

Respond with ONLY a JSON object (no markdown, no explanation) in this format:
{{
    "intent": "<one of: nutrition_question, food_lookup, meal_suggestion>",
    "food_name": "<food item if mentioned or referenced from prior context, else null>",
    "quantity_g": <quantity in grams if mentioned or referenced, else null>,
    "ingredients": [<list of ingredients if mentioned or referenced, else empty list>],
    "reasoning": "<brief one-line reason for your classification>"
}}

INTENT DEFINITIONS:
- "nutrition_question": General questions about nutrition, diet, health, food comparisons, or follow-ups.
  Examples: "Is rice good for weight loss?", "What about brown rice?", "Why is that?"
  
- "food_lookup": User wants specific nutrition values for a food item.
  Examples: "How many calories in 200g rice?", "Nutrition in 2 eggs", "What about 300g of that?"
  Note: Resolve pronouns and follow-ups from context (e.g., if previous conversation was about chicken, and user says "what about 200g of it?", food_name is "chicken").
  Convert counts to grams (1 egg ≈ 50g, 1 banana ≈ 118g, 1 apple ≈ 182g, 1 slice bread ≈ 30g, 1 cup milk ≈ 244g, 1 cup rice ≈ 185g).

- "meal_suggestion": User wants meal ideas, recipes, or what to cook with ingredients.
  Examples: "I have eggs and rice, what can I make?", "Give me another idea with those ingredients", "Add tomatoes to that recipe"
"""


# ─── Step 2: Run the Agent ───────────────────────────────────

def run_agent(user_message: str, chat_history: list = None) -> dict:
    """
    Main agent function. This is the entry point called by app.py.

    The agent loop:
        1. Send user message to Gemini to detect intent
        2. Based on intent, call the right tool (or no tool)
        3. Build the final response using LLM + tool data

    Args:
        user_message: What the user typed.
        chat_history: Previous messages for context.

    Returns:
        A dict with:
            - "response": The text answer to show the user
            - "intent": What the agent detected
            - "tool_used": Which tool was called (or "none")
            - "tool_result": Raw data from the tool (if any)
    """
    # Check if Gemini is configured
    client = get_client()
    if client is None:
        return {
            "response": (
                "⚠️ **API key not configured.**\n\n"
                "Please add your Google API key to the `.env` file:\n"
                "```\nGOOGLE_API_KEY=your_actual_key_here\n```\n"
                "Get a free key at: https://aistudio.google.com/apikey"
            ),
            "intent": "error",
            "tool_used": "none",
            "tool_result": None,
        }

    try:
        model_name = "gemini-3.5-flash-lite"

        # Format recent history for context
        history_text = _format_history(chat_history)

        # ── Step 1: Detect intent (context-aware) ──
        intent_query = INTENT_PROMPT.format(
            history_text=history_text if history_text else "None (first turn)",
            user_message=user_message,
        )
        intent_response = client.models.generate_content(
            model=model_name,
            contents=intent_query,
        )
        intent_data = _parse_intent(intent_response.text)

        intent = intent_data.get("intent", "nutrition_question")
        tool_used = "none"
        tool_result = None

        # ── Step 2: Call the appropriate tool ──

        if intent == "food_lookup":
            food_name = intent_data.get("food_name", "")
            quantity = intent_data.get("quantity_g") or 100
            if food_name:
                tool_result = tool_food_lookup(food_name, float(quantity))
                tool_used = "food_lookup"
            else:
                # No food name detected — treat as a general question
                intent = "nutrition_question"

        elif intent == "meal_suggestion":
            ingredients = intent_data.get("ingredients", [])
            if ingredients:
                tool_result = tool_meal_suggestion(ingredients)
                tool_used = "meal_suggestion"
            else:
                # No ingredients — still let the LLM suggest something
                tool_used = "meal_suggestion (general)"

        # ── Step 3: Generate final response ──
        response_text = _generate_response(
            client, model_name, user_message, intent, tool_result, chat_history
        )

        return {
            "response": response_text,
            "intent": intent,
            "tool_used": tool_used,
            "tool_result": tool_result,
            "reasoning": intent_data.get("reasoning", ""),
        }

    except Exception as e:
        error_msg = str(e)

        # Friendly messages for common errors
        if "API_KEY_INVALID" in error_msg or "401" in error_msg:
            friendly = "❌ **Invalid API key.** Please check your `.env` file."
        elif "RATE_LIMIT" in error_msg or "429" in error_msg:
            friendly = "⏳ **Rate limit hit.** Please wait a moment and try again."
        elif "quota" in error_msg.lower():
            friendly = "📊 **API quota exceeded.** Check your Google AI Studio dashboard."
        else:
            friendly = f"❌ **Something went wrong:** {error_msg}"

        return {
            "response": friendly,
            "intent": "error",
            "tool_used": "none",
            "tool_result": None,
        }


# ─── Helper: Parse Intent JSON ──────────────────────────────

def _parse_intent(raw_text: str) -> dict:
    """
    Parse the LLM's intent classification response.

    The LLM should return JSON, but sometimes it wraps it in
    markdown code blocks. This function handles both cases.
    """
    text = raw_text.strip()

    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        text = "\n".join(lines)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # If JSON parsing fails, default to nutrition_question
        return {
            "intent": "nutrition_question",
            "food_name": None,
            "quantity_g": None,
            "ingredients": [],
            "reasoning": "Could not parse intent — defaulting to general question.",
        }


def _format_history(chat_history: list | None, max_turns: int = 6) -> str:
    """Format recent chat messages into a readable conversation transcript."""
    if not chat_history:
        return ""
    recent = chat_history[-max_turns:]
    lines = []
    for msg in recent:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "").strip()
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


# ─── Helper: Generate Final Response ────────────────────────

def _generate_response(
    client, model_name: str, user_message: str, intent: str,
    tool_result: dict | None, chat_history: list | None
) -> str:
    """
    Use the LLM to generate the final user-facing response.
    All modes include recent conversation history so follow-ups and
    contextual questions are answered naturally.
    """
    history_text = _format_history(chat_history)
    history_block = f"Recent conversation:\n{history_text}\n\n" if history_text else ""

    if intent == "food_lookup" and tool_result:
        if "error" in tool_result:
            prompt = f"""{SYSTEM_PROMPT}

{history_block}The user asked: "{user_message}"

The food lookup tool returned an error: {tool_result['error']}
Available foods in our database: {tool_result.get('available_foods', 'none')}

Respond helpfully taking into account any prior conversation context.
Tell the user the food wasn't found, show what's available, and offer alternatives."""
        else:
            prompt = f"""{SYSTEM_PROMPT}

{history_block}The user asked: "{user_message}"

Here is the EXACT nutrition data from our database (DO NOT change these numbers):

Food: {tool_result['food']}
Quantity: {tool_result['quantity_g']}g
Note: {tool_result['serving_note']}
Calories: {tool_result['calories']} kcal
Protein: {tool_result['protein_g']}g
Carbohydrates: {tool_result['carbs_g']}g
Fat: {tool_result['fat_g']}g
Fiber: {tool_result['fiber_g']}g

Present this data to the user clearly.
If this was a follow-up or comparison to previous messages, acknowledge the context.
Use the EXACT numbers above — do not round or change them.
Add a brief helpful comment about the food's nutrition profile."""

    elif intent == "meal_suggestion" and tool_result:
        found = tool_result.get("found_ingredients", [])
        missing = tool_result.get("missing_ingredients", [])

        found_summary = "\n".join(
            [f"- {f['name']}: {f['calories']} cal, {f['protein_g']}g protein, "
             f"{f['carbs_g']}g carbs, {f['fat_g']}g fat (per 100g)"
             for f in found]
        )

        prompt = f"""{SYSTEM_PROMPT}

{history_block}The user asked: "{user_message}"

Ingredients found in our database (nutrition per 100g):
{found_summary if found_summary else "None found"}

Ingredients NOT in our database: {', '.join(missing) if missing else 'None'}

Based on these ingredients and any previous conversation preferences, suggest ONE practical meal. Include:
1. Meal name
2. Brief recipe (5 steps or fewer)
3. Suggested quantity for each ingredient (in grams)
4. Approximate total nutrition (calculate from the per-100g data above, clearly mark as ESTIMATED)
5. One tip about why this meal is a good choice

If some ingredients are missing from the database, you can still suggest the meal
but note that nutrition for those items is estimated.
Keep it practical and beginner-friendly."""

    else:
        # General nutrition question or conversational follow-up
        prompt = f"""{SYSTEM_PROMPT}

{history_block}User: {user_message}

Answer the user's nutrition question naturally, keeping the ongoing conversation in mind.
Be helpful, practical, and concise.
If they ask about specific calorie/protein numbers for a food, suggest using the food lookup feature for exact values.
Do not invent specific nutrition numbers."""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    return response.text
