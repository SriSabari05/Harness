# 🥗 NutriGuide AI — Personal Nutrition Assistant

A beginner-friendly AI agent that answers nutrition questions, looks up food data, and suggests meals — built with Python, Streamlit, and Google Gemini.

## What It Does

| Feature | How It Works |
|---------|-------------|
| **💬 Nutrition Q&A** | Ask any food/nutrition question → LLM answers directly |
| **🔍 Food Lookup** | Name a food + quantity → Agent looks up real data, Python calculates values |
| **🍳 Meal Suggestion** | List your ingredients → Agent checks DB + LLM suggests a recipe |

### What Makes It an "Agent"?

Unlike a basic chatbot that just forwards your message to an LLM, this app uses an **agent loop**:

```
User message
    ↓
1. UNDERSTAND — LLM classifies intent (Q&A? Lookup? Meal suggestion?)
    ↓
2. ACT — Agent calls the right tool with extracted parameters
    ↓
3. OBSERVE — Tool returns real data (from local database, not LLM)
    ↓
4. RESPOND — LLM formats the tool results into a helpful answer
```

The LLM does the **thinking**. Python does the **math**. This prevents hallucinated nutrition numbers.

## Project Structure

```
NutriGuideAI/
├── app.py               # Streamlit UI — chat interface
├── agent.py             # AI agent — intent detection, tool routing, response generation
├── nutrition_tools.py   # Tools — food lookup calculator, meal ingredient checker
├── food_database.py     # Local database — 15 common foods with real nutrition data
├── requirements.txt     # Python dependencies
├── .env                 # API key (not committed to git)
└── .gitignore           # Git ignore rules
```

## Setup

### 1. Install Python 3.9+

Download from [python.org](https://www.python.org/downloads/) if you don't have it.

### 2. Install dependencies

```bash
cd NutriGuideAI
pip install -r requirements.txt
```

### 3. Get a free Google API key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the key

### 4. Add your key to `.env`

Open `.env` and replace the placeholder:

```
GOOGLE_API_KEY=AIzaSy...your_actual_key...
```

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**.

## Example Conversations

**Food Lookup:**
> "How much protein in 200g chicken?"
>
> Agent detects intent → `food_lookup` → calls `tool_food_lookup("chicken", 200)` → calculates from database → presents results.

**Nutrition Q&A:**
> "Is rice bad for weight loss?"
>
> Agent detects intent → `nutrition_question` → no tool needed → LLM answers directly.

**Meal Suggestion:**
> "I have eggs, rice, and tomatoes. Suggest a healthy dinner."
>
> Agent detects intent → `meal_suggestion` → calls `tool_meal_suggestion(["eggs", "rice", "tomatoes"])` → checks database → LLM suggests a recipe with estimated nutrition.

## Foods in the Database

Rice, Chicken Breast, Egg, Banana, Milk, Bread, Potato, Apple, Paneer, Dal, Oats, Tomato, Onion, Spinach, Yogurt

All values are per 100g, sourced from USDA FoodData Central (approximate).

## Safety

- Does NOT diagnose medical conditions
- Does NOT recommend extreme diets or supplements
- Marks all estimates clearly
- Recommends consulting professionals for medical diet needs

## License

Educational project — built for learning AI agent development.
