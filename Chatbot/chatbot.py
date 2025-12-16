import streamlit as st
from llm.chatollama import ChatOllamaBot
import time

# Ensure username exists
if "username" not in st.session_state:
    st.session_state.username = "User"

st.title("Chatbot")
st.caption("Ask me about classes, meetings, sections, and more!")

bot = ChatOllamaBot(st.session_state.username)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"Hello **{st.session_state.username}**! How can I help you today?",
        }
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask something...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        response = bot.chat(prompt)
        typed = ""

        for chunk in response.split():
            typed += chunk + " "
            time.sleep(0.03)
            placeholder.markdown(typed + "▌")

        placeholder.markdown(typed)
        st.session_state.messages.append({"role": "assistant", "content": typed})
