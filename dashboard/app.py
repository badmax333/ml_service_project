import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API URL
API_URL = "http://backend:8000"

st.set_page_config(
    page_title="ML Transcription Service",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ ML Service for Audio Transcription")
st.markdown("---")

# Sidebar для авторизации
st.sidebar.title("🔐 Авторизация")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None

# Форма входа/регистрации
with st.sidebar.expander("Вход / Регистрация", expanded=not st.session_state.token):
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            response = requests.post(
                f"{API_URL}/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                st.session_state.token = response.json()["access_token"]
                st.session_state.user = email
                st.rerun()
            else:
                st.error("Login failed")
    
    with tab2:
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_fullname = st.text_input("Full Name", key="reg_fullname")
        if st.button("Register"):
            response = requests.post(
                f"{API_URL}/auth/register",
                json={"email": reg_email, "password": reg_password, "full_name": reg_fullname}
            )
            if response.status_code == 201:
                st.success("Registration successful! Please login.")
            else:
                st.error("Registration failed")

if st.session_state.token:
    st.sidebar.success(f"✅ Logged in as: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

# Основной контент (только для авторизованных)
if st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Информация о пользователе
    st.subheader("👤 User Info")
    try:
        response = requests.get(f"{API_URL}/users/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            col1, col2, col3 = st.columns(3)
            col1.metric("Email", user["email"])
            col2.metric("Balance", f"{user['balance']} credits")
            col3.metric("Role", user["role"])
    except:
        st.warning("User info endpoint not available yet")
    
    st.markdown("---")
    
    # Транскрибация аудио
    st.subheader("🎤 Transcribe Audio")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        model_size = st.selectbox(
            "Select Model",
            options=["tiny", "base", "small"],
            format_func=lambda x: {
                "tiny": "🪶 Tiny (5 credits)",
                "base": "📘 Base (15 credits)",
                "small": "🐘 Small (30 credits)"
            }[x]
        )
    
    with col2:
        audio_file = st.file_uploader(
            "Upload audio file",
            type=["mp3", "wav", "ogg", "m4a"]
        )
    
    if audio_file and st.button("Transcribe"):
        files = {"file": (audio_file.name, audio_file.getvalue(), audio_file.type)}
        response = requests.post(
            f"{API_URL}/transcribe/{model_size}",
            headers=headers,
            files=files
        )
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ {result['message']}")
            st.info(f"Job ID: {result['job_id']}")
        else:
            st.error(f"Transcription failed: {response.text}")
    
    st.markdown("---")
    
    # История транскрибаций
    st.subheader("📜 Transcription History")
    
    if st.button("Refresh History"):
        response = requests.get(f"{API_URL}/transcribe/jobs", headers=headers)
        if response.status_code == 200:
            jobs = response.json()
            if jobs:
                df = pd.DataFrame(jobs)
                df["created_at"] = pd.to_datetime(df["created_at"])
                df = df.rename(columns={
                    "id": "ID",
                    "model_size": "Model",
                    "status": "Status",
                    "transcribed_text": "Text",
                    "credits_cost": "Cost",
                    "duration_seconds": "Duration (s)",
                    "created_at": "Created"
                })
                st.dataframe(df[["ID", "Model", "Status", "Cost", "Duration (s)", "Created"]])
                
                # Показать текст для выбранной транскрибации
                selected_id = st.selectbox("Select job to view text", df["ID"].tolist())
                selected_job = df[df["ID"] == selected_id].iloc[0]
                if selected_job["Status"] == "completed":
                    st.text_area("Transcribed Text", selected_job["Text"], height=200)
            else:
                st.info("No transcription jobs yet")
        else:
            st.error("Failed to load history")
else:
    st.info("👈 Please login or register to use the service")
