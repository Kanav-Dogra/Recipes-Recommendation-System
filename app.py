import streamlit as st
from recommendation import load_data, recommend_recipes, normalize_ingredient
import time

# Page config with favicon
st.set_page_config(
    page_title="🍽️ Smart Recipe Recommender", 
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': "https://github.com/your-repo/issues",
        'About': "# � Smart Recipe Recommender\nFind perfect recipes for your ingredients!"
    }
)

# Custom CSS for animations and styling
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    :root {
        --primary: #FF6B6B;
        --secondary: #4ECDC4;
        --accent: #FFE66D;
        --light: #F7FFF7;
        --dark: #292F36;
    }
    
    body {
        font-family: 'Poppins', sans-serif;
        background-color: #f9f9f9;
        color: var(--dark);
    }
    
    .title-container {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.2);
        color: white;
        text-align: center;
        animation: fadeInDown 0.8s ease;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .input-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
        animation: fadeIn 0.8s ease;
    }
    
    .stTextInput input {
        border: 2px solid var(--secondary) !important;
        border-radius: 12px !important;
        padding: 12px 15px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.2) !important;
    }
    
    .result-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        border-left: 5px solid var(--primary);
        animation: fadeInUp 0.5s ease;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.12);
    }
    
    .match {
        color: #28a745 !important;
        font-weight: bold;
        background-color: #e6f7e6;
        padding: 2px 6px;
        border-radius: 4px;
        border-left: 3px solid #28a745;
    }
    
    .match-percentage {
        color: #28a745 !important;
        font-weight: bold;
    }
    
    .progress-container {
        height: 6px;
        background: #e0e0e0;
        border-radius: 3px;
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 3px;
        background: linear-gradient(90deg, var(--secondary), var(--primary));
        transition: width 0.4s ease;
    }
    
    .gif-container {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .title-container {
            padding: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Load CSS
load_css()

# Title with animated gradient
st.markdown("""
    <div class="title-container">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🍳 Smart Recipe Recommender</h1>
        <p style="margin: 0.5rem 0 0; font-size: 1.1rem; opacity: 0.9;">
        Discover delicious recipes based on what's in your kitchen!
        </p>
    </div>
""", unsafe_allow_html=True)

# GIF Display Section
st.markdown("""
<div class="gif-container">
    <img src="https://i.pinimg.com/originals/a8/e2/f7/a8e2f7d95211306cbef9e89766402abc.gif" width="300" style="border-radius: 15px;">
</div>
""", unsafe_allow_html=True)

# Input section with animation
with st.container():
    st.markdown("""
    <div class="input-container">
        <h3 style="color: var(--dark); margin-top: 0;">🔍 What ingredients do you have?</h3>
    """, unsafe_allow_html=True)
    
    user_input = st.text_input(
        "Enter ingredients (comma separated):", 
        "",
        key="ingredient_input",
        placeholder="e.g., chicken, tomatoes, onions, garlic",
        help="Separate ingredients with commas"
    )
    
    st.markdown("<p style='text-align: center; color: #666; font-size: 0.9rem;'>Try: eggs, flour, milk or rice, chicken, vegetables</p>", 
                unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

user_ingredients = [normalize_ingredient(i.strip()) for i in user_input.split(",") if i.strip()]

# Session state setup
if "page" not in st.session_state:
    st.session_state.page = 0
if "last_input" not in st.session_state:
    st.session_state.last_input = ""
if "cached_results" not in st.session_state:
    st.session_state.cached_results = []
if "search_executed" not in st.session_state:
    st.session_state.search_executed = False

# Search button with loading animation
col1, col2, col3 = st.columns([1,2,1])
with col2:
    search_clicked = st.button("🧑‍🍳 Find Recipes", use_container_width=True)

# If search clicked or input changed
if search_clicked or (user_input and user_input != st.session_state.last_input):
    st.session_state.search_executed = True
    st.session_state.page = 0
    st.session_state.last_input = user_input
    
    with st.spinner("Searching for the best recipes..."):
        # Simulate loading with progress bar
        progress_bar = st.empty()
        for percent_complete in range(100):
            time.sleep(0.01)
            progress_bar.markdown(f"""
                <div class="progress-container">
                    <div class="progress-bar" style="width: {percent_complete + 1}%"></div>
                </div>
            """, unsafe_allow_html=True)
        
        df = load_data()
        st.session_state.cached_results = recommend_recipes(user_input, df, top_n=None)
        progress_bar.empty()

# Show recommendations or empty state
if st.session_state.search_executed:
    results = st.session_state.cached_results
    RECIPES_PER_PAGE = 5
    
    if user_input and user_ingredients:
        if results:
            total_pages = (len(results) - 1) // RECIPES_PER_PAGE + 1
            start_idx = st.session_state.page * RECIPES_PER_PAGE
            end_idx = min(start_idx + RECIPES_PER_PAGE, len(results))
            visible_results = results[start_idx:end_idx]

            st.markdown("""
                <h2 style="text-align: center; color: var(--dark); margin: 1.5rem 0; 
                border-bottom: 2px solid var(--secondary); padding-bottom: 0.5rem;">
                🧾 Recommended Recipes
                </h2>
            """, unsafe_allow_html=True)

            for idx, (name, score, ingredients, instructions) in enumerate(visible_results):
                matched_set = set(ingredients) & set(user_ingredients)
                highlighted_ingredients = []
                
                for ing in ingredients:
                    if ing in matched_set:
                        highlighted_ingredients.append(f"<span class='match'>{ing}</span>")
                    else:
                        highlighted_ingredients.append(ing)

                with st.container():
                    st.markdown(f"""
                        <div class='result-card'>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h3 style="color: var(--primary); margin: 0;">🍲 {name}</h3>
                                <div style="background: #f0f0f0; padding: 5px 10px; border-radius: 20px;" class="match-percentage">
                                    {round(score * 100)}% Match
                                </div>
                            </div>
                            <div style="margin-top: 1rem;">
                                <p><b style="color: var(--secondary);">📋 Ingredients:</b></p>
                                <div style="background: #f9f9f9; padding: 10px; border-radius: 8px; 
                                margin-bottom: 10px;">
                                    {', '.join(highlighted_ingredients)}
                                </div>
                                <p><b style="color: var(--secondary);">📖 Instructions:</b></p>
                                <div style="background: #f9f9f9; padding: 10px; border-radius: 8px;">
                                    {instructions}
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    recipe_text = f"""
                    🍽️ Recipe: {name}
                    ✅ Match Score: {round(score * 100)}%
                    
                    📋 Ingredients:
                    {', '.join(ingredients)}

                    📜 Instructions:
                    {instructions}
                    """

                    col1, col2 = st.columns([3,1])
                    with col2:
                        st.download_button(
                            label="📥 Download Recipe",
                            data=recipe_text.strip(),
                            file_name=f"{name.replace(' ', '_')}.txt",
                            mime="text/plain",
                            key=f"dl_{name}_{idx}",
                            use_container_width=True
                        )

            # Pagination controls
            if total_pages > 1:
                st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if st.button("⬅️ Previous", key="prev_button", disabled=(st.session_state.page == 0)):
                        if st.session_state.page > 0:
                            st.session_state.page -= 1
                            st.rerun()

                with col3:
                    if st.button("Next ➡️", key="next_button", disabled=(st.session_state.page == total_pages - 1)):
                        if st.session_state.page < total_pages - 1:
                            st.session_state.page += 1
                            st.rerun()

                with col2:
                    st.markdown(
                        f"<div style='text-align:center; padding-top: 0.4rem; color: #777;'>"
                        f"Page {st.session_state.page + 1} of {total_pages}</div>",
                        unsafe_allow_html=True
                    )
        else:
            st.markdown("""
                <div style="text-align: center; padding: 3rem; background-color: #FFF5F5; 
                border-radius: 15px; margin: 2rem 0;">
                <h3 style="color: var(--primary);">😕 No recipes found</h3>
                <p style="color: #555;">We couldn't find any recipes matching your ingredients.</p>
                <p>Try different combinations or check your spelling!</p>
                </div>
            """, unsafe_allow_html=True)
    elif user_input and not user_ingredients:
        st.warning("Please enter valid ingredients separated by commas")