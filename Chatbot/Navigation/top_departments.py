import streamlit as st
import pandas as pd
import requests

st.title("Top Departments by Section")

API_URL = "http://127.0.0.1:5000/lacy/api/stats/top-departments-by-sections"

semester = st.sidebar.selectbox("Semester", ["All", "Fall", "Spring", "V1", "V2"])
year = st.sidebar.selectbox("Year", ["All", "Choose a year"])
if year == "Choose a year":
    year = st.sidebar.number_input(
        "Select Year", min_value=2000, max_value=2100, value=2025
    )
else:
    year = "All"

limit = st.sidebar.slider("Limit", 1, 3, 5)

params = {}

if semester != "All":
    params["semester"] = semester

if year != "All":
    params["year"] = year

params["limit"] = limit


try:
    resp = requests.get(API_URL, params=params)

    if resp.status_code == 200:
        data = resp.json()

        if len(data) == 0:
            st.info("No data to display.")
        else:
            df = pd.DataFrame(data)

            # FIX: use real backend column names
            df = df.set_index("fullcode")["sections"]

            col = st.container()

            with col:
                st.subheader("Bar Chart")
                st.bar_chart(df)

            with col:
                st.subheader("Line Chart")
                st.line_chart(df)

            with col:
                st.subheader("Area Chart")
                st.area_chart(df)

    else:
        st.error(f"Error {resp.status_code}: {resp.text}")

except Exception as e:
    st.error(f"Error contacting the backend: {e}")
