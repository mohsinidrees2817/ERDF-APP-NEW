import streamlit as st
from auth import create_user, login_user


def show_login():
    st.title("Login to ERDF Tool")

    mode = st.radio("Select Mode", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if mode == "Sign Up":
            if create_user(email, password):
                st.success("Account created. You can now log in.")
            else:
                st.error("Email already registered.")
        else:  # Login
            if login_user(email, password):
                st.session_state["user"] = email
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials.")
