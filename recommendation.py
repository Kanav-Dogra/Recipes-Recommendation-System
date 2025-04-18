#!/usr/bin/env python
# coding: utf-8

# In[1]:


# recommendation.py
import pandas as pd
import ast
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter

# 🔧 Enhanced ingredient normalization
def normalize_ingredient(ingredient):
    ingredient = ingredient.lower().strip()
    ingredient = re.sub(r'[^\w\s]', '', ingredient)  # remove punctuation
    ingredient = re.sub(r'\s+', ' ', ingredient)     # normalize spaces
    
    # Better singularization with common plural endings
    plural_endings = {
        's': '',
        'es': 'e',
        'ies': 'y'
    }
    for ending, replacement in plural_endings.items():
        if ingredient.endswith(ending) and len(ingredient) > len(ending):
            ingredient = ingredient[:-len(ending)] + replacement
            break
            
    # Common ingredient substitutions
    substitutions = {
        'tomato': 'tomatoes',
        'potato': 'potatoes',
        'leaf': 'leaves'
    }
    return substitutions.get(ingredient, ingredient)

# 📦 Enhanced data loading with TF-IDF
def load_data():
    try:
        df = pd.read_csv("Food Ingredients and Recipe Dataset with Image Name Mapping.csv")
        df = df[['Title', 'Cleaned_Ingredients', 'Instructions']].dropna()
        
        # Convert ingredient strings to lists
        df['Cleaned_Ingredients'] = df['Cleaned_Ingredients'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
        
        # Normalize ingredients
        df['Cleaned_Ingredients'] = df['Cleaned_Ingredients'].apply(
            lambda ings: [normalize_ingredient(ing) for ing in ings if ing.strip()])
        
        # Create TF-IDF vectorizer
        df['ingredients_str'] = df['Cleaned_Ingredients'].apply(lambda x: ' '.join(x))
        global vectorizer, tfidf_matrix
        vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split(), lowercase=False)
        tfidf_matrix = vectorizer.fit_transform(df['ingredients_str'])
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=['Title', 'Cleaned_Ingredients', 'Instructions'])

# 🧮 Enhanced similarity scoring
def calculate_scores(user_ingredients, df):
    # TF-IDF cosine similarity
    user_input_str = ' '.join(user_ingredients)
    user_vec = vectorizer.transform([user_input_str])
    tfidf_scores = cosine_similarity(user_vec, tfidf_matrix).flatten()
    
    # Jaccard similarity
    jaccard_scores = []
    user_set = set(user_ingredients)
    for ings in df['Cleaned_Ingredients']:
        recipe_set = set(ings)
        intersection = user_set & recipe_set
        union = user_set | recipe_set
        jaccard_scores.append(len(intersection) / len(union) if union else 0)
    
    # Ingredient coverage score
    coverage_scores = []
    for ings in df['Cleaned_Ingredients']:
        recipe_set = set(ings)
        common = user_set & recipe_set
        coverage_scores.append(len(common) / len(recipe_set) if recipe_set else 0)
    
    # Combine scores with weights
    combined_scores = (
        0.5 * tfidf_scores + 
        0.3 * np.array(jaccard_scores) + 
        0.2 * np.array(coverage_scores)
    )
    
    return combined_scores

# 🍽 Enhanced recommendation function
def recommend_recipes(user_input, df, top_n=10):
    try:
        user_ingredients = [normalize_ingredient(i) for i in user_input.split(",") if i.strip()]
        if not user_ingredients:
            return []
            
        scores = calculate_scores(user_ingredients, df)
        
        results = []
        for idx in (-scores).argsort()[:top_n if top_n else len(scores)]:
            if scores[idx] > 0:  # Only include recipes with some match
                results.append((
                    df.iloc[idx]['Title'],
                    scores[idx],
                    df.iloc[idx]['Cleaned_Ingredients'],
                    df.iloc[idx]['Instructions']
                ))
        
        return results
    except Exception as e:
        print(f"Error in recommendation: {e}")
        return []

# In[2]:





