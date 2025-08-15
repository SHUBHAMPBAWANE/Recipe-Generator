import streamlit as st
import openai

# --- OpenAI Setup ---
openai.api_key = "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"  # Use secrets or .env in production

# --- Streamlit UI ---
st.title("🍳 AI Recipe Generator")
st.markdown("Enter your ingredients and I'll create a recipe for you!")

ingredients = st.text_input("🧂 Ingredients (comma separated):")

if st.button("Generate Recipe"):
    with st.spinner("Cooking up something delicious..."):
        prompt = f"""
        I have the following ingredients: {ingredients}.
        Generate a unique recipe using these ingredients. 
        Suggest 2 alternative ingredients. 
        Also, estimate total calories per serving.
        Return the result in the following format:
        - Recipe Name
        - Ingredients
        - Instructions
        - Alternatives
        - Estimated Calories
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        reply = response['choices'][0]['message']['content']
        st.markdown("### 🍽️ Here's your recipe:")
        st.markdown(reply)
