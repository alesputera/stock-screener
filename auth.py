import streamlit as st
import hashlib

def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

def load_users():
    """
    Ambil user dari Streamlit Secrets
    Format:
    USERS = {
      "sandro": "md5hash",
      "admin": "md5hash"
    }
    """
    return st.secrets.get("USERS", {})

def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔐 Login Required")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        hashed = hash_password(password)

        if username in users and users[username] == hashed:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Login berhasil")
            st.rerun()
        else:
            st.error("Username / password salah")

    return False
