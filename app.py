import streamlit as st
from google import genai
import os
import time
import json

# ---------------------------
# USER AUTHENTICATION SYSTEM
# ---------------------------

USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = password
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    return username in users and users[username] == password

# ---------------------------
# STREAMLIT UI
# ---------------------------

st.title("🎓 GCE Bodi Assistant")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ✅ ONLY ONE SELECTBOX (Fix)
menu = st.sidebar.selectbox(
    "Menu",
    ["Login", "Register"],
    key="main_menu"
)

# ---------------------------
# REGISTER PAGE
# ---------------------------

if menu == "Register" and not st.session_state.logged_in:
    st.subheader("Create Account")

    new_user = st.text_input("Username", key="register_username")
    new_pass = st.text_input("Password", type="password", key="register_password")

    if st.button("Register", key="register_btn"):
        if new_user == "" or new_pass == "":
            st.error("All fields required!")
        elif len(new_pass) < 6:
            st.error("Password must be at least 6 characters")
        elif register_user(new_user, new_pass):
            st.success("Registration successful! Please login.")
        else:
            st.error("Username already exists")

# ---------------------------
# LOGIN PAGE
# ---------------------------

elif menu == "Login" and not st.session_state.logged_in:
    st.subheader("Login")

    user = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_btn"):
        if login_user(user, password):
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# ---------------------------
# CHATBOT (AFTER LOGIN)
# ---------------------------

if st.session_state.logged_in:

    st.sidebar.success("Logged In ✅")

    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.rerun()

    # 🔐 USE ENVIRONMENT VARIABLE (Safer)
    API_KEY = "YOUR_API_KEY"

    if not API_KEY:
        st.error("API key not found. Set GEMINI_API_KEY environment variable.")
        st.stop()

    client = genai.Client(api_key=API_KEY)

    FILES_TO_UPLOAD = {
        "GCE_Knowledge": "gce_bodi_data.txt",
        "GCE_Mandatory": "Mandatory Disclosure.pdf"
    }

    def get_all_files():
        uploaded_refs = []
        existing_cloud_files = {f.display_name: f for f in client.files.list()}

        for display_name, local_path in FILES_TO_UPLOAD.items():
            if not os.path.exists(local_path):
                continue

            if (
                display_name in existing_cloud_files and
                existing_cloud_files[display_name].state.name == "ACTIVE"
            ):
                uploaded_refs.append(existing_cloud_files[display_name])
            else:
                uploaded = client.files.upload(
                    file=local_path,
                    config={'display_name': display_name}
                )
                while uploaded.state.name == "PROCESSING":
                    time.sleep(2)
                    uploaded = client.files.get(name=uploaded.name)
                uploaded_refs.append(uploaded)

        return uploaded_refs

    all_context_files = get_all_files()

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Ask about GCE Bodi..."):
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )
        st.chat_message("user").write(prompt)

        input_contents = all_context_files + [prompt]

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=input_contents,
            config={
                "system_instruction": 
                "You are the GCE Bodi Assistant. Use attached files to answer."
            }
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": response.text}
        )

        st.chat_message("assistant").write(response.text)
