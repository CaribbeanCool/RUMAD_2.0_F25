import streamlit as st
import re

from API.dao.user import UserDAO

dao = UserDAO()


# Sign up page
def sign_up_ui():
    with st.form(key="signup", clear_on_submit=True):
        st.subheader("Sign Up")

        username = st.text_input("Username", placeholder="Choose a username")
        password1 = st.text_input(
            "Password", placeholder="Enter a password", type="password"
        )
        password2 = st.text_input(
            "Confirm Password", placeholder="Confirm your password", type="password"
        )

        submitted = st.form_submit_button("Sign up")

        if submitted:
            ok, message = validate_signup(username, password1, password2)

            if ok:
                dao.insertUser(username, password1)
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Account created successfully!")
                st.rerun()
            else:
                st.warning(message)


# Log in page
def log_in_ui():
    with st.form(key="login", clear_on_submit=True):
        st.subheader("Log In")

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input(
            "Password", placeholder="Enter your password", type="password"
        )

        submitted = st.form_submit_button("Log in")

        if submitted:
            ok, message = validate_login(username, password)

            if ok:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.warning(message)


# Validation functions
def validate_signup(username, pass1, pass2):
    if len(username) < 2:
        return False, "Username must be at least 2 characters long."

    if not re.match("^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."

    if dao.getUserByUsername(username):
        return False, "Username already exists."

    if len(pass1) < 6:
        return False, "Password must be at least 6 characters long."

    if pass1 != pass2:
        return False, "Passwords do not match."

    return True, "OK"


def validate_login(username, password):
    result = dao.verifyUser(username, password)

    if result is None:
        return False, "Username does not exist."

    if result == -1:
        return False, "Incorrect password."

    return True, "OK"


# Switch pages
option = st.selectbox("Sign up / Log in", ("Sign up", "Log in"))

if option == "Sign up":
    sign_up_ui()
else:
    log_in_ui()
