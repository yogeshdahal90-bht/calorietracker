import streamlit as st
import google.generativeai as genai
import plotly.express as px
import pandas as pd
from datetime import datetime
import json

# 1. Setup Gemini - Using the most stable model name
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('models/gemini-1.5-flash')

# 2. Your Metrics
DOB = datetime(1993, 5, 11)
HEIGHT = 162 
WEIGHT = 81.7
AGE = (datetime.now() - DOB).days // 365
BMR = (10 * WEIGHT) + (6.25 * HEIGHT) - (5 * AGE) + 5

st.set_page_config(page_title="80kg Tracker", layout="centered")

# 3. Header & BMR
st.title("🎯 Goal: 80kg")
st.write(f"**Age:** {AGE} | **Height:** {HEIGHT}cm | **Current:** {WEIGHT}kg")
st.metric("Daily BMR Target", f"{int(BMR)} kcal")

# 4. Storage
if 'logs' not in st.session_state:
    st.session_state.logs = []

# 5. The "Brain" Function with Error Handling
def parse_entry(text):
    prompt = f"""
    Return ONLY a JSON object for this food/activity: "{text}"
    Rules:
    1. Format: {{"item": "string", "calories": number, "type": "Food" or "Activity"}}
    2. 'Proteas Maize' = 140 per cup. 'Datchi' = 200.
    3. If activity, calories must be NEGATIVE.
    4. No extra text, just the JSON.
    """
    try:
        response = model.generate_content(prompt)
        # Clean the response string in case Gemini adds markdown backticks
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        st.error(f"Error parsing entry: {e}")
        return None

# 6. User Input
with st.form(key='input_form', clear_on_submit=True):
    user_text = st.text_input("Log something (e.g., '100g ramen' or 'walked 500 steps')")
    submit_button = st.form_submit_button(label='Enter')

if submit_button and user_text:
    entry = parse_entry(user_text)
    if entry:
        st.session_state.logs.append(entry)
        st.rerun()

# 7. Visualization
if st.session_state.logs:
    df = pd.DataFrame(st.session_state.logs)
    food_df = df[df['calories'] > 0]
    
    if not food_df.empty:
        fig = px.pie(food_df, values='calories', names='item', hole=0.4)
        st.plotly_chart(fig)
    
    net_cals = df['calories'].sum()
    st.subheader(f"Total Net Calories: {net_cals}")
    
    if st.button("Reset for Tomorrow"):
        st.session_state.logs = []
        st.rerun()
