"""Optional Streamlit UI to browse sample catalog rows (no API keys required)."""

import pandas as pd
import streamlit as st

data = {
    "Product": ["Green Tea", "Black Tea", "Herbal Tea"],
    "Price": [10, 15, 20],
    "Ingredients": ["Green tea leaves", "Black tea leaves", "Herbal mix"],
    "Certifications": ["Organic", "Fair Trade", "Non-GMO"],
    "Nutrients": ["Antioxidants", "Caffeine", "Vitamins"],
}
df = pd.DataFrame(data)

st.title("EasyCompare — sample catalog (Streamlit)")
st.write("Static sample table for quick UI demos. The Telegram bot uses RAG + OCR + OpenAI.")
st.dataframe(df)

selected = st.multiselect("Select products to compare", df["Product"])
if selected:
    st.write("Comparison of selected products:")
    st.dataframe(df[df["Product"].isin(selected)])
