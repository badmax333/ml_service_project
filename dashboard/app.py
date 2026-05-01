import streamlit as st
import requests
import pandas as pd

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
    st.session_state.captcha_id = None
    st.session_state.question = None

# Форма входа/регистрации
with st.sidebar.expander("Вход / Регистрация", expanded=not st.session_state.token):
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": email, "password": password},
                    timeout=10
                )
                if response.status_code == 200:
                    st.session_state.token = response.json()["access_token"]
                    st.session_state.user = email
                    st.rerun()
                else:
                    st.error("Login failed")
            except Exception as e:
                st.error(f"Connection error: {e}")

    with tab2:
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_fullname = st.text_input("Full Name", key="reg_fullname")
        if st.button("Register"):
            try:
                response = requests.post(
                    f"{API_URL}/auth/register",
                    json={"email": reg_email, "password": reg_password, "full_name": reg_fullname},
                    timeout=10
                )
                if response.status_code == 201:
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed")
            except Exception as e:
                st.error(f"Connection error: {e}")

if st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Информация о пользователе
    st.sidebar.success(f"✅ Logged in as: {st.session_state.user}")
    
    # Пополнение баланса
    st.sidebar.markdown("---")
    st.sidebar.subheader("💰 Top Up Balance")
    
    # Кнопка генерации капчи
    if st.sidebar.button("🔄 Generate Captcha"):
        try:
            captcha_response = requests.get(f"{API_URL}/billing/captcha", headers=headers, timeout=10)
            if captcha_response.status_code == 200:
                captcha_data = captcha_response.json()
                st.session_state.captcha_id = captcha_data["captcha_id"]
                st.session_state.question = captcha_data["question"]
                st.sidebar.success("✅ Captcha generated!")
                st.rerun()
            else:
                st.sidebar.error(f"❌ HTTP {captcha_response.status_code}")
        except Exception as e:
            st.sidebar.error(f"❌ Error: {e}")
    
    # Показываем капчу если есть
    if st.session_state.get("question"):
        st.sidebar.write(f"**Question:** {st.session_state.question}")
        captcha_answer = st.sidebar.number_input("Your answer", key="captcha_answer", step=1, value=0)
        amount = st.sidebar.number_input("Amount (credits)", min_value=1, max_value=10000, value=100, key="topup_amount")
        
        if st.sidebar.button("💸 Top Up"):
            try:
                response = requests.post(
                    f"{API_URL}/billing/topup",
                    headers=headers,
                    json={
                        "amount": amount,
                        "captcha_id": st.session_state.captcha_id,
                        "answer": captcha_answer
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.sidebar.success(f"✅ {result['message']}")
                    st.session_state.question = None
                    st.rerun()
                else:
                    try:
                        error_msg = response.json().get("detail", f"HTTP {response.status_code}")
                    except:
                        error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                    st.sidebar.error(f"❌ {error_msg}")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.question = None
        st.rerun()
    
    # Основной контент
    st.subheader("👤 User Info")
    try:
        response = requests.get(f"{API_URL}/users/me", headers=headers, timeout=10)
        if response.status_code == 200:
            user = response.json()
            col1, col2, col3 = st.columns(3)
            col1.metric("Email", user["email"])
            col2.metric("Balance", f"{user['balance']} credits")
            col3.metric("Role", user["role"])
    except:
        st.warning("Could not fetch user info")
    
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
    
    if audio_file and st.button("🎙️ Transcribe"):
        try:
            files = {"file": (audio_file.name, audio_file.getvalue(), audio_file.type)}
            response = requests.post(
                f"{API_URL}/transcribe/{model_size}",
                headers=headers,
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ {result['message']}")
                st.info(f"Job ID: {result['job_id']}")
            else:
                st.error(f"Transcription failed: {response.text[:200]}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # История транскрибаций
    st.subheader("📜 Transcription History")
    
    if st.button("🔄 Refresh History"):
        try:
            response = requests.get(f"{API_URL}/transcribe/jobs", headers=headers, timeout=10)
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
                    st.dataframe(df[["ID", "Model", "Status", "Cost", "Duration (s)", "Created"]], use_container_width=True)
                    
                    if "Text" in df.columns and df["Text"].notna().any():
                        completed_df = df[df["Status"] == "completed"]
                        if not completed_df.empty:
                            selected_id = st.selectbox("Select job to view text", completed_df["ID"].tolist())
                            selected_job = df[df["ID"] == selected_id].iloc[0]
                            if selected_job.get("Text"):
                                st.text_area("Transcribed Text", selected_job["Text"], height=200)
                else:
                    st.info("No transcription jobs yet")
            else:
                st.error(f"Failed to load history: HTTP {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("👈 Please login or register to use the service")