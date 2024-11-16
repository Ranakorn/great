import streamlit as st
import pandas as pd
from pinotdb import connect
import plotly.express as px
import time

# ตั้งค่าการรีเฟรช
st.sidebar.header("Settings")
refresh_interval_sec = st.sidebar.slider("Refresh Interval (milliseconds)", 1, 60, 1)
refresh_interval_ms = refresh_interval_sec  # ค่าในมิลลิวินาที

# ฟังก์ชันดึงข้อมูล
@st.cache_data(ttl=30)  # ใช้ cache_data เพื่อเก็บข้อมูลในระยะเวลา
def fetch_data(query):
    conn = connect(host='46.137.234.15', port=8099, path='/query/sql', schema='http')
    curs = conn.cursor()
    curs.execute(query)
    return [row for row in curs.fetchall()]

# Query 1: Total Revenue by Food Type
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
    total_revenue DESC
'''
data1 = fetch_data(query1)
df1 = pd.DataFrame(data1, columns=['food_type', 'total_orders', 'total_revenue'])

# Query 2: Page Views Count by Menu and Hour
query2 = '''
SELECT 
    menu_name,
    COUNT(userid) AS page_views_count,
    FLOOR(viewtime / 3600) AS hour_of_day
FROM 
    Visit_food_3
GROUP BY 
    menu_name, hour_of_day
'''
data2 = fetch_data(query2)
df2 = pd.DataFrame(data2, columns=['menu_name', 'page_views_count', 'hour_of_day'])
df2['formatted_viewtime'] = pd.to_datetime(df2['hour_of_day'], unit='h').dt.strftime('%d/%m/%Y %H:%M')

# Query 3: Gender Distribution
query3 = '''
SELECT 
    gender,
    COUNT(userid) AS user_count
FROM 
    Users_2
GROUP BY 
    gender
'''
data3 = fetch_data(query3)
df3 = pd.DataFrame(data3, columns=['gender', 'user_count'])

# Query 4: User Count by Region
query4 = '''
SELECT 
    regionid,
    COUNT(userid) AS region_count
FROM 
    Users_2
GROUP BY 
    regionid
ORDER BY 
    region_count DESC
'''
data4 = fetch_data(query4)
df4 = pd.DataFrame(data4, columns=['Region ID', 'User Count'])

# Layout การแสดงผล
st.title("Real-Time Data Dashboard")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# กราฟในแต่ละช่อง
with col1:
    st.subheader("Total Revenue by Food Type")
    fig1 = px.bar(df1, x='food_type', y='total_revenue', color='food_type', 
                  title="Total Revenue by Food Type")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Page Views Count by Menu and Hour")
    fig2 = px.bar(df2, x='page_views_count', y='menu_name', color='menu_name', 
                  orientation='h', barmode='stack', 
                  title="Page Views Count by Menu and Hour")
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    st.subheader("Gender Distribution")
    fig3 = px.pie(df3, names='gender', values='user_count', hole=0.3, 
                  title="Gender Distribution")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("User Count by Region")
    st.dataframe(df4.style.set_table_styles(
        [
            {'selector': 'thead th', 'props': [('background-color', '#f2f2f2'), ('padding', '8px')]},
            {'selector': 'tbody td', 'props': [('padding', '8px')]},
            {'selector': 'table', 'props': [('width', '100%')]},
        ]
    ).set_properties(**{'text-align': 'center'}))

# การรีเฟรชหน้าเว็บอัตโนมัติ
time.sleep(refresh_interval_ms / 1000)  # แปลงมิลลิวินาทีเป็นวินาที
st.rerun()
