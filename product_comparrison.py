import streamlit as st
import pandas as pd

# Sample product data
data = {
    'Product': ['Green Tea', 'Black Tea', 'Herbal Tea'],
    'Price': [10, 15, 20],
    'Ingredients': ['Green tea leaves', 'Black tea leaves', 'Herbal mix'],
    'Certifications': ['Organic', 'Fair Trade', 'Non-GMO'],
    'Nutrients': ['Antioxidants', 'Caffeine', 'Vitamins']
}
df = pd.DataFrame(data)

st.title('Aldi Scan & Compare App')

# Display the dataframe
st.write('Here are the products:')
st.dataframe(df)

# Select products to compare
selected_products = st.multiselect('Select products to compare', df['Product'])

if selected_products:
    st.write('Comparison of selected products:')
    st.dataframe(df[df['Product'].isin(selected_products)])
