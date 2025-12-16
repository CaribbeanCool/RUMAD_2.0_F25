import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Classes without Prerequisites", layout="wide")
st.title("Classes without Prerequisites")

API_URL = "http://127.0.0.1:5000/lacy/api/stats/classes-without-prereqs"

try:
    resp = requests.get(API_URL, timeout=10)

    if resp.status_code == 200:
        data = resp.json()

        if len(data) == 0:
            st.info("No classes without prerequisites found.")
        else:
            df = pd.DataFrame(data)

            df = df.set_index("fullcode")

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
        st.error(f"Error from the backend: {resp.text}")

except Exception as e:
    st.error(f"Error contacting the backend: {e}")
