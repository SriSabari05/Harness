# ──────────────────────────────────────────────────────────────
# app.py — NutriGuide AI  •  Streamlit Interface
# ──────────────────────────────────────────────────────────────
# This is the file you run:  streamlit run app.py
#
# It creates a simple chat interface where users type messages
# and the AI agent processes them, picks the right tool, and
# responds with real nutrition data.
# ──────────────────────────────────────────────────────────────

import streamlit as st
from agent import run_agent
from food_database import list_all_foods

# ─── Page Config (must be first Streamlit call) ──────────────

st.set_page_config(
    page_title="NutriGuide AI",
    page_icon="🥗",
    layout="centered",
)

# ─── Session State ───────────────────────────────────────────
# Streamlit re-runs this entire file on every interaction.
# session_state is how we keep data between re-runs.

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─── Sidebar ─────────────────────────────────────────────────

with st.sidebar:
    st.markdown("# 🥗 NutriGuide AI")
    st.caption("Your Personal Nutrition Assistant")

    st.divider()

    st.markdown("### What I Can Do")
    st.markdown(
        """
        **💬 Nutrition Q&A**
        Ask anything about food & nutrition.

        **🔍 Food Lookup**
        Get exact nutrition for any food + quantity.

        **🍳 Meal Suggestions**
        Tell me your ingredients — I'll suggest a meal.
        """
    )

    st.divider()

    st.markdown("### Try These")
    st.code("How much protein in 200g chicken?", language=None)
    st.code("Is rice good for weight loss?", language=None)
    st.code("I have eggs, tomato, and onion.\nSuggest a meal.", language=None)

    st.divider()

    # Show available foods
    with st.expander("📋 Foods in Database"):
        for food in list_all_foods():
            st.markdown(f"• {food.title()}")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ─── Main Chat Area ──────────────────────────────────────────

st.title("🥗 NutriGuide AI")
st.caption("Ask me about nutrition, look up food data, or get meal suggestions!")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show agent info (which tool it picked) for assistant messages
        if message["role"] == "assistant" and "agent_info" in message:
            info = message["agent_info"]
            with st.expander("🤖 Agent Details", expanded=False):
                st.markdown(f"**Intent Detected:** `{info.get('intent', 'unknown')}`")
                st.markdown(f"**Tool Used:** `{info.get('tool_used', 'none')}`")
                if info.get("reasoning"):
                    st.markdown(f"**Reasoning:** {info['reasoning']}")
                if info.get("tool_result"):
                    st.json(info["tool_result"])

# ─── Chat Input ──────────────────────────────────────────────

user_input = st.chat_input("Ask me anything about nutrition...")

if user_input:
    # 1. Show the user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
    })
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Run the agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = run_agent(user_input, st.session_state.chat_history)

        # Display the response
        st.markdown(result["response"])

        # Show agent decision details
        if result["intent"] != "error":
            with st.expander("🤖 Agent Details", expanded=False):
                st.markdown(f"**Intent Detected:** `{result.get('intent', 'unknown')}`")
                st.markdown(f"**Tool Used:** `{result.get('tool_used', 'none')}`")
                if result.get("reasoning"):
                    st.markdown(f"**Reasoning:** {result['reasoning']}")
                if result.get("tool_result"):
                    st.json(result["tool_result"])

    # 3. Save assistant response
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result["response"],
        "agent_info": {
            "intent": result.get("intent"),
            "tool_used": result.get("tool_used"),
            "reasoning": result.get("reasoning", ""),
            "tool_result": result.get("tool_result"),
        },
    })

# ─── Footer ──────────────────────────────────────────────────

st.divider()
st.caption(
    "⚠️ NutriGuide AI provides general nutrition information only. "
    "Not a substitute for professional dietary or medical advice."
)
