import streamlit as st
import google.generativeai as genai
import plotly.express as px
import pandas as pd
from datetime import datetime

# 1. Setup Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

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

# 4. Storage & Reset Logic
if 'logs' not in st.session_state:
    st.session_state.logs = []

# 5. The "Brain" Function
def parse_entry(text):
    prompt = f"""
    You are a nutrition assistant for a user aiming for 80kg. 
    Convert the following text into a JSON object: {{"item": "name", "calories": number, "type": "Food" or "Activity"}}.
    Note: 'Proteas Maize' is ~140kcal per cup. 'Datchi' with sandwich cheese is ~200kcal per portion. 
    If it's an activity, make calories a negative number.
    Text: "{text}"
    """
    response = model.generate_content(prompt)
    return eval(response.text.strip().replace('```json', '').replace('```', ''))

# 6. User Input
user_text = st.text_input("Log something (e.g., '100g ramen' or 'walked 500 steps')", key="input")

if st.button("Enter"):
    if user_text:
        entry = parse_entry(user_text)
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
