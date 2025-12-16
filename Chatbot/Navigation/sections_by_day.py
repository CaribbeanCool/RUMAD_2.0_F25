import streamlit as st
import pandas as pd
import requests


st.title("Sections by day")

API_URL = "http://127.0.0.1:5000/lacy/api/stats/sections-by-day"

semester = st.sidebar.selectbox("Semester", ["All", "Fall", "Spring", "V1", "V2"])
year = st.sidebar.selectbox("Year", ["All", "Choose a year"])
if year == "Choose a year":
    year = st.sidebar.number_input(
        "Select Year", min_value=2000, max_value=2100, value=2025
    )
else:
    year = "All"

params = {}

if semester != "All":
    params["semester"] = semester

if year != "All":
    params["year"] = year

resp = requests.get(API_URL, params=params)


if resp.status_code == 200:
    data = resp.json()

    if len(data) == 0:
        st.info("Data was not found.")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(data)

        weekdays = ["L", "M", "W", "J", "V", "S", "D"]

        df["day"] = pd.Categorical(df["day"], categories=weekdays, ordered=True)
        df = df.sort_values("day")

        df = df.set_index("day")["sections"]

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
