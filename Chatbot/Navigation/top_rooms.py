import streamlit as st

import pandas as pd
import requests

st.set_page_config(page_title="Top Rooms by Average Utilization", layout="wide")
st.title("Top Rooms by Average Utilization")

semester = st.sidebar.selectbox("Semester", ["All", "Fall", "Spring", "V1", "V2"])
year = st.sidebar.selectbox("Year", ["All", "Choose a year"])
if year == "Choose a year":
    year = st.sidebar.number_input(
        "Select Year", min_value=2000, max_value=2100, value=2025
    )
else:
    year = "All"

limit = st.sidebar.slider("Limit", 1, 10, 5)

API_URL = "http://127.0.0.1:5000/lacy/api/stats/top-rooms-by-utilization"

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
            st.info("No rooms found.")
        else:
            df = pd.DataFrame(data)

            df["room"] = df["building"] + "-" + df["room_number"]

            df = df.sort_values(by="utilization", ascending=False)

            df["room"] = pd.Categorical(df["room"], categories=df["room"], ordered=True)

            df = df.set_index("room")["utilization"]

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

            st.dataframe(df)

    else:
        st.error(f"Error from the backend: {resp.text}")

except Exception as e:
    st.error(f"Error contacting the backend: {e}")
