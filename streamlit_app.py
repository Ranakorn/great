import pandas as pd
from pinotdb import connect
import plotly.express as px
import streamlit as st
from datetime import datetime
import time

# การตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(layout="wide")

# การเชื่อมต่อกับฐานข้อมูล Pinot
conn = connect(host='46.137.234.15', port=8099, path='/query/sql', schema='http')
curs = conn.cursor()

# การ query ข้อมูล
curs.execute('''SELECT 
    food_type, 
    COUNT(*) AS total_orders, 
    SUM(price) AS total_revenue
FROM 
    Visit_food_3
GROUP BY 
    food_type
ORDER BY 
    total_revenue DESC;
''')
tables = [row for row in curs.fetchall()]

# สร้าง DataFrame
df = pd.DataFrame(tables, columns=['food_type', 'total_orders', 'total_revenue'])

# สร้างกราฟแท่งที่แสดง total_revenue โดยแยกสีตาม food_type
fig1 = px.bar(df, 
              x='food_type', 
              y='total_revenue', 
              title="Total Revenue by Food Type", 
              labels={'total_revenue': 'Total Revenue', 'food_type': 'Food Type'},
              color='food_type',  # แยกสีตามประเภทอาหาร
              height=350)

# การ query ข้อมูลของเมนูและชั่วโมง
curs.execute('''SELECT 
    menu_name,
    COUNT(userid) AS page_views_count,
    FLOOR(viewtime / 3600) AS hour_of_day
FROM 
    "Visit_food_3"
GROUP BY 
    menu_name, hour_of_day
''')

# รับข้อมูลจากผลลัพธ์ query
tables2 = [row for row in curs.fetchall()]

# สร้าง DataFrame
df2 = pd.DataFrame(tables2, columns=['menu_name', 'page_views_count', 'hour_of_day'])

# แปลง hour_of_day เป็นเวลาในรูปแบบ dd/MM/yyyy HH:mm
df2['formatted_viewtime'] = pd.to_datetime(df2['hour_of_day'], unit='h').dt.strftime('%d/%m/%Y %H:%M')

# สร้างกราฟแท่งแนวนอน (horizontal bar chart) และแสดงสะสม (stacked)
fig2 = px.bar(df2, 
              x='page_views_count', 
              y='menu_name', 
              color='menu_name', 
              title="Page Views Count by Menu and Hour (Stacked)",
              labels={'page_views_count': 'Page Views Count', 'menu_name': 'Food Menu'},
              orientation='h',  # ใช้แท่งแนวนอน
              barmode='stack',  # สะสมสีของแต่ละประเภทอาหาร
              height=350)

# การ query ข้อมูลจาก Users_2 สำหรับ gender
curs.execute('''SELECT 
    gender,
    COUNT(userid) AS user_count
FROM 
    "Users_2"
GROUP BY 
    gender
;''')

# รับข้อมูลจากผลลัพธ์ query
tables3 = [row for row in curs.fetchall()]

# สร้าง DataFrame จากผลลัพธ์ที่ได้
df3 = pd.DataFrame(tables3, columns=['gender', 'user_count'])

# สร้างกราฟโดนัท (pie chart with hole)
fig3 = px.pie(df3, 
              names='gender', 
              values='user_count', 
              hole=0.3,  # กำหนดขนาดของ hole เพื่อให้เป็นโดนัท
              title="Gender Distribution")

# การ query ข้อมูลจาก Users_2 สำหรับ region
curs.execute('''SELECT 
    regionid,
    COUNT(userid) AS region_count
FROM 
    "Users_2"
GROUP BY 
    regionid
ORDER BY 
    region_count DESC
;''')

# รับข้อมูลจากผลลัพธ์ query
tables4 = [row for row in curs.fetchall()]

# สร้าง DataFrame
df4 = pd.DataFrame(tables4, columns=['Region ID', 'User Count'])

# รีเซ็ต index และลบหมายเลขแถว
df4 = df4.reset_index(drop=True)

# การตกแต่งตารางโดยไม่มีเส้นขอบ
styled_df = df4.style.set_table_styles(
    [
        # ตกแต่งหัวตาราง
        {'selector': 'thead th', 'props': [('background-color', '#f2f2f2'), ('padding', '8px')]},
        
        # ตกแต่งเนื้อหาของตาราง
        {'selector': 'tbody td', 'props': [('padding', '8px')]},
        
        # กำหนดให้ตารางเต็มหน้าจอ
        {'selector': 'table', 'props': [('width', '100%')]},
    ]
).set_properties(
    **{'text-align': 'center'}
)

# ตัวเลือกสำหรับการรีเฟรชข้อมูล
refresh_rate = st.slider('Set Refresh Rate (seconds)', min_value=1, max_value=60, value=5)

# การแบ่งคอลัมน์เพื่อแสดงกราฟและตาราง
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# ใช้ empty container สำหรับการรีเฟรชข้อมูล
while True:
    with col1:
        st.plotly_chart(fig2, use_container_width=True, key="fig2")

    with col2:
        st.plotly_chart(fig1, use_container_width=True, key="fig1")

    with col3:
        st.plotly_chart(fig3, use_container_width=True, key="fig3")

    with col4:
        st.write("Region Distribution")
        st.dataframe(styled_df)

    time.sleep(refresh_rate)
    st.rerun()  # รีเฟรชหน้าจอ
