import pandas as pd
import plotly.express as px
import streamlit as st
from pinotdb import connect
from datetime import datetime

# Function to get data from Pinot
def get_data_from_pinot(query):
    try:
        # Connect to Pinot
        conn = connect(host='46.137.234.15', port=8099, path='/query/sql', schema='http')
        curs = conn.cursor()
        curs.execute(query)
        
        # Fetch data and return as a DataFrame
        tables = [row for row in curs.fetchall()]
        df = pd.DataFrame(tables)
        return df
    except Exception as e:
        st.error(f"Error fetching data from Pinot: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Streamlit App

# Title of the app
st.title("Food Orders Analysis")

# Total Revenue by Food Type
st.header("Total Revenue by Food Type")
query1 = '''
    SELECT 
        food_type, 
        COUNT(*) AS total_orders, 
        SUM(price) AS total_revenue
    FROM 
        Visit_food_3
    GROUP BY 
        food_type
    ORDER BY 
        total_revenue DESC;
'''
df1 = get_data_from_pinot(query1)

# Check if DataFrame is empty
if df1.empty:
    st.error("No data available for Total Revenue by Food Type.")
else:
    # Ensure the correct column names
    df1.columns = ['food_type', 'total_orders', 'total_revenue']

    # Create the bar chart
    fig1 = px.bar(df1, 
                  x='food_type', 
                  y='total_revenue', 
                  title="Total Revenue by Food Type", 
                  labels={'total_revenue': 'Total Revenue', 'food_type': 'Food Type'},
                  color='food_type',  
                  height=400)
    st.plotly_chart(fig1)
