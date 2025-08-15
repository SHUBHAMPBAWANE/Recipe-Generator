# AI-Enhanced Recipe Generator using Streamlit + Firebase + TF-IDF (Updated for Your Dataset)

import streamlit as st
import pandas as pd
import random
import firebase_admin
from firebase_admin import credentials, firestore
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ========== Firebase Setup (Safe from reinitialization) ==========
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ========== Load and Process Dataset ==========
df = pd.read_csv("indian_food.csv")
df.dropna(subset=['ingredients', 'name'], inplace=True)
df['ingredients'] = df['ingredients'].str.lower().str.replace('[^\w\s,]', '', regex=True)
df['ingredient_string'] = df['ingredients'].apply(lambda x: ' '.join(x.split(', ')))

# TF-IDF Vectorization
tfidf = TfidfVectorizer()
ingredient_vectors = tfidf.fit_transform(df['ingredient_string'])

# ========== AI Recipe Finder ==========
def find_ai_recipe(user_ingredients, meal_type):
    filtered_df = df[df['meal'].str.lower() == meal_type.lower()]
    if filtered_df.empty:
        return None

    tfidf_filtered = TfidfVectorizer()
    filtered_df['ingredient_string'] = filtered_df['ingredients'].apply(lambda x: ' '.join(x.split(', ')))
    ingredient_vectors_filtered = tfidf_filtered.fit_transform(filtered_df['ingredient_string'])

    user_input = ' '.join(user_ingredients)
    user_vec = tfidf_filtered.transform([user_input])
    similarities = cosine_similarity(user_vec, ingredient_vectors_filtered)
    index = similarities.argmax()
    return filtered_df.iloc[index].to_dict()

# ========== Firebase Helpers ==========
def save_to_firebase(recipe):
    doc_ref = db.collection("recipes").add(recipe)
    return doc_ref

def fetch_saved_recipes():
    try:
        docs = db.collection("recipes").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        st.error(f"Failed to fetch saved recipes: {e}")
        return []

# ========== Streamlit UI ==========
st.title("🍲 AI-Powered Indian Recipe Generator")

meal_type = st.selectbox("Select Meal", ["Breakfast", "Lunch", "Dinner"])
num = st.number_input("Number of ingredients", 1, 10, 3)
user_ingredients = [st.text_input(f"Ingredient {i+1}").strip().lower() for i in range(num)]
user_ingredients = [ing for ing in user_ingredients if ing]

if st.button("Generate Recipe"):
    recipe = find_ai_recipe(user_ingredients, meal_type)
    if recipe:
        st.session_state.generated_recipe = recipe
        st.subheader(f"🌟 {recipe['name']}")
        st.markdown("*Ingredients:* " + recipe['ingredient_string'])
        st.markdown("*Instructions:*")
        st.markdown(recipe['instructions'])
    else:
        st.warning("No matching recipe found.")

recipe = st.session_state.get("generated_recipe", None)

if st.button("Save to My Cookbook"):
    if recipe:
        try:
            save_to_firebase(recipe)
            st.success("✅ Recipe saved to Firebase!")
        except Exception as e:
            st.error(f"❌ Failed to save recipe: {e}")
    else:
        st.warning("Generate a recipe before saving.")

with st.expander("📚 View My Saved Recipes"):
    saved_recipes = fetch_saved_recipes()
    if saved_recipes:
        for i, saved in enumerate(saved_recipes, 1):
            st.markdown(f"### {i}. 🌟 {saved['name']}")
            st.markdown("*Ingredients:* " + saved.get('ingredient_string', ''))
            st.markdown("*Instructions:*")
            st.markdown(saved.get('instructions', ''))
            st.markdown("---")
    else:
        st.info("No recipes saved yet.")