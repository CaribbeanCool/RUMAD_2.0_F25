import streamlit as st

import pandas as pd
import requests

st.set_page_config(page_title="Longest Average Duration", layout="wide")
st.title("Longest Average meeting durations")


semester = st.sidebar.selectbox("Semester", ["All", "Fall", "Spring", "V1", "V2"])
year = st.sidebar.selectbox("Year", ["All", "Choose a year"])
if year == "Choose a year":
    year = st.sidebar.number_input(
        "Select Year", min_value=2000, max_value=2100, value=2025
    )
else:
    year = "All"

limit = st.sidebar.slider("Number of courses", 1, 10, 5)

API_URL = "http://127.0.0.1:5000/lacy/api/stats/top-classes-by-avg-duration"


params = {}

if semester != "All":
    params["semester"] = semester

if year != "All":
    params["year"] = year

params["limit"] = limit


try:
    resp = requests.get(API_URL, params=params, timeout=10)

    if resp.status_code == 200:
        data = resp.json()

        if len(data) == 0:
            st.info("No courses found.")
        else:
            df = pd.DataFrame(data)

            df = df.sort_values(by="average_minutes", ascending=False)

            df["fullcode"] = pd.Categorical(
                df["fullcode"], categories=df["fullcode"], ordered=True
            )

            df = df.set_index("fullcode")["average_minutes"]

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
