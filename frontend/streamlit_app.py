import streamlit as st
import requests
import os
from datetime import datetime
import time
from streamlit_cookies_manager import EncryptedCookieManager
import json

st.set_page_config(
    page_title="The Monk AI | Divine Wisdom",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None,
)

cookies = EncryptedCookieManager(
    password=os.getenv("COOKIE_SECRET", "change-this-cookie-secret-in-env"),
)
if not cookies.ready():
    st.stop()

API_BASE_URL = "http://localhost:8000"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "user_mode" not in st.session_state:
    st.session_state.user_mode = "beginner"
if "animation_played" not in st.session_state:
    st.session_state.animation_played = False
if "typing_indicator" not in st.session_state:
    st.session_state.typing_indicator = False

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Playfair+Display:wght@400;500;600;700&family=Poppins:wght@300;400;500;600&display=swap');

:root {
    --primary-gold: #D4AF37;
    --primary-orange: #FF6B35;
    --deep-saffron: #E85D04;
    --spiritual-purple: #7B2CBF;
    --divine-blue: #1A365D;
    --light-cream: #FFF8F0;
    --warm-white: #FFFAF5;
    --dark-text: #2D3436;
    --soft-gold: #F4E4BA;
}

* {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f 0%, #12122a0a0a 30%, #0d1b2a 70%, #1a1a2e 100%);
    min-height: 100vh;
}

/* Animated Background */
.animated-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
}

.animated-bg::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: 
        radial-gradient(circle at 20% 80%, rgba(255, 107, 53, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 80% 20%, rgba(123, 44, 191, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 40% 40%, rgba(212, 175, 55, 0.08) 0%, transparent 30%),
        radial-gradient(circle at 60% 70%, rgba(232, 93, 4, 0.1) 0%, transparent 35%);
    animation: aurora 25s ease-in-out infinite;
}

.animated-bg::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%' height='100%' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    animation: grain 8s steps(10) infinite;
}

@keyframes aurora {
    0%, 100% { transform: translate(0, 0) rotate(0deg) scale(1); }
    25% { transform: translate(2%, 2%) rotate(1deg) scale(1.02); }
    50% { transform: translate(0, 4%) rotate(0deg) scale(1); }
    75% { transform: translate(-2%, 2%) rotate(-1deg) scale(0.98); }
}

@keyframes grain {
    0%, 100% { transform: translate(0, 0); }
    10% { transform: translate(-5%, -10%); }
    20% { transform: translate(-15%, 5%); }
    30% { transform: translate(7%, -25%); }
    40% { transform: translate(-5%, 25%); }
    50% { transform: translate(-15%, 10%); }
    60% { transform: translate(15%, 0%); }
    70% { transform: translate(0%, 15%); }
    80% { transform: translate(3%, 35%); }
    90% { transform: translate(-10%, 10%); }
}

/* Floating Elements */
.floating-elements {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: -1;
    overflow: hidden;
}

.floating-om {
    position: absolute;
    font-size: 28px;
    opacity: 0;
    animation: floatUp 20s linear infinite;
    color: #D4AF37;
    text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
}

.floating-om:nth-child(1) { left: 5%; animation-delay: 0s; }
.floating-om:nth-child(2) { left: 15%; animation-delay: 3s; }
.floating-om:nth-child(3) { left: 25%; animation-delay: 6s; }
.floating-om:nth-child(4) { left: 35%; animation-delay: 9s; }
.floating-om:nth-child(5) { left: 45%; animation-delay: 12s; }
.floating-om:nth-child(6) { left: 55%; animation-delay: 15s; }
.floating-om:nth-child(7) { left: 65%; animation-delay: 2s; }
.floating-om:nth-child(8) { left: 75%; animation-delay: 5s; }
.floating-om:nth-child(9) { left: 85%; animation-delay: 8s; }
.floating-om:nth-child(10) { left: 95%; animation-delay: 11s; }

@keyframes floatUp {
    0% { 
        transform: translateY(100vh) scale(0.5) rotate(0deg);
        opacity: 0;
    }
    10% { opacity: 0.15; }
    90% { opacity: 0.15; }
    100% { 
        transform: translateY(-100px) scale(1.2) rotate(360deg);
        opacity: 0;
    }
}

/* Main Title with Animation */
.title-container {
    text-align: center;
    margin-bottom: 3rem;
    animation: fadeInDown 1s ease-out;
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-50px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.main-title {
    font-family: 'Playfair Display', serif;
    font-size: 5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #D4AF37 0%, #F4E4BA 30%, #FF6B35 60%, #D4AF37 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite, titleFloat 6s ease-in-out infinite;
    text-shadow: 0 0 80px rgba(212, 175, 55, 0.4);
    margin-bottom: 0.5rem;
}

@keyframes shimmer {
    to { background-position: 200% center; }
}

@keyframes titleFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.main-subtitle {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8rem;
    color: rgba(255, 255, 255, 0.6);
    text-align: center;
    font-weight: 400;
    letter-spacing: 6px;
    text-transform: uppercase;
    animation: fadeIn 1.5s ease-out 0.3s both;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Auth Container */
.auth-container {
    max-width: 420px;
    margin: 0 auto;
    padding: 2.5rem;
    background: rgba(10, 10, 20, 0.7);
    backdrop-filter: blur(30px);
    border-radius: 30px;
    border: 1px solid rgba(212, 175, 55, 0.15);
    box-shadow: 
        0 30px 60px rgba(0, 0, 0, 0.5),
        0 0 100px rgba(212, 175, 55, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.9);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.auth-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    background: rgba(0, 0, 0, 0.3);
    padding: 0.4rem;
    border-radius: 15px;
}

.auth-tab {
    flex: 1;
    padding: 0.8rem;
    text-align: center;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.95rem;
}

.auth-tab.active {
    background: linear-gradient(135deg, #FF6B35, #E85D04);
    color: white;
    box-shadow: 0 4px 20px rgba(255, 107, 53, 0.4);
    transform: scale(1.02);
}

.auth-tab:not(.active):hover {
    color: rgba(255, 255, 255, 0.8);
    background: rgba(255, 255, 255, 0.05);
}

/* Form Elements */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(212, 175, 55, 0.2) !important;
    border-radius: 12px !important;
    color: white !important;
    padding: 0.8rem 1rem !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #FF6B35 !important;
    background: rgba(255, 255, 255, 0.06) !important;
    box-shadow: 0 0 25px rgba(255, 107, 53, 0.2) !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: rgba(255, 255, 255, 0.3) !important;
}

.stSelectbox > div > div > div {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(212, 175, 55, 0.2) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* Buttons */
.monk-button {
    width: 100%;
    padding: 1rem 2rem;
    background: linear-gradient(135deg, #D4AF37 0%, #F4E4BA 40%, #FF6B35 60%, #D4AF37 100%);
    background-size: 300% 100%;
    border: none;
    border-radius: 15px;
    color: #0a0a0f;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.4s ease;
    text-transform: uppercase;
    letter-spacing: 2px;
    position: relative;
    overflow: hidden;
    animation: buttonShimmer 3s linear infinite;
}

@keyframes buttonShimmer {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.monk-button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 20px 50px rgba(212, 175, 55, 0.5);
}

.monk-button:active {
    transform: translateY(-1px) scale(0.99);
}

/* Chat Interface */
.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.2rem 2rem;
    background: rgba(10, 10, 20, 0.8);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(212, 175, 55, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}

.chat-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    background: linear-gradient(135deg, #D4AF37, #F4E4BA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Chat Messages */
.chat-container {
    max-width: 850px;
    margin: 0 auto;
    padding: 2rem;
    padding-bottom: 180px;
    min-height: calc(100vh - 200px);
}

.message-wrapper {
    display: flex;
    margin-bottom: 1.2rem;
    animation: messageSlide 0.4s ease-out;
}

@keyframes messageSlide {
    from { 
        opacity: 0; 
        transform: translateY(30px) scale(0.95);
    }
    to { 
        opacity: 1; 
        transform: translateY(0) scale(1);
    }
}

.message-wrapper.user { justify-content: flex-end; }
.message-wrapper.assistant { justify-content: flex-start; }

.message-bubble {
    max-width: 75%;
    padding: 1.2rem 1.6rem;
    border-radius: 22px;
    position: relative;
    line-height: 1.7;
    transition: all 0.3s ease;
}

.message-bubble:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3) !important;
}

.user-message {
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.95), rgba(232, 93, 4, 0.85));
    color: #0a0a0f;
    border-bottom-right-radius: 5px;
    box-shadow: 0 10px 30px rgba(255, 107, 53, 0.35);
}

.assistant-message {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(15px);
    color: rgba(255, 255, 255, 0.95);
    border-bottom-left-radius: 5px;
    border: 1px solid rgba(212, 175, 55, 0.15);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.message-role {
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 0.6rem;
    opacity: 0.6;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

/* Response Cards */
.response-section {
    margin-top: 1rem;
    padding: 1.2rem;
    background: rgba(255, 255, 255, 0.025);
    border-radius: 16px;
    border-left: 3px solid #FF6B35;
    animation: fadeIn 0.4s ease-out 0.2s both;
}

.hindi-translation {
    background: linear-gradient(135deg, rgba(123, 44, 191, 0.15), rgba(155, 89, 182, 0.08));
    border-left: 3px solid #7B2CBF;
    padding: 1.2rem;
    border-radius: 14px;
    margin: 1rem 0;
    color: rgba(255, 255, 255, 0.9);
    animation: fadeIn 0.5s ease-out 0.3s both;
}

.citation-card {
    background: rgba(255, 107, 53, 0.08);
    border: 1px solid rgba(255, 107, 53, 0.2);
    border-radius: 14px;
    padding: 1rem;
    margin: 0.6rem 0;
    transition: all 0.3s ease;
    animation: fadeIn 0.4s ease-out 0.4s both;
}

.citation-card:hover {
    background: rgba(255, 107, 53, 0.12);
    transform: translateX(5px);
    border-color: rgba(255, 107, 53, 0.4);
}

.citation-book {
    color: #FF6B35;
    font-weight: 600;
    font-size: 0.95rem;
}

.recommendation-card {
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.12), rgba(129, 199, 132, 0.06));
    border: 1px solid rgba(76, 175, 80, 0.25);
    border-radius: 14px;
    padding: 1.2rem;
    margin-top: 1rem;
    animation: fadeIn 0.5s ease-out 0.5s both;
}

.keyword-card {
    margin: 0.5rem 0;
    padding: 0.8rem 1rem;
    background: rgba(212, 175, 55, 0.08);
    border-radius: 10px;
    border-left: 3px solid #D4AF37;
    transition: all 0.3s ease;
    animation: fadeIn 0.4s ease-out 0.35s both;
}

.keyword-card:hover {
    background: rgba(212, 175, 55, 0.12);
    transform: translateX(3px);
}

/* Input Area */
.input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1.2rem 1.5rem;
    background: rgba(10, 10, 20, 0.92);
    backdrop-filter: blur(30px);
    border-top: 1px solid rgba(212, 175, 55, 0.1);
    z-index: 100;
}

.input-wrapper {
    max-width: 850px;
    margin: 0 auto;
    display: flex;
    gap: 1rem;
    align-items: flex-end;
}

.chat-input {
    flex: 1;
    padding: 1rem 1.4rem;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(212, 175, 55, 0.15);
    border-radius: 25px;
    color: white;
    font-size: 1rem;
    resize: none;
    min-height: 55px;
    max-height: 120px;
    transition: all 0.3s ease;
}

.chat-input:focus {
    outline: none;
    border-color: #D4AF37;
    background: rgba(255, 255, 255, 0.06);
    box-shadow: 0 0 30px rgba(212, 175, 55, 0.15);
}

.send-button {
    width: 55px;
    height: 55px;
    border-radius: 50%;
    background: linear-gradient(135deg, #FF6B35, #E85D04);
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    box-shadow: 0 5px 25px rgba(255, 107, 53, 0.4);
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 5px 25px rgba(255, 107, 53, 0.4); }
    50% { box-shadow: 0 5px 35px rgba(255, 107, 53, 0.6); }
}

.send-button:hover {
    transform: scale(1.1);
    box-shadow: 0 8px 40px rgba(255, 107, 53, 0.6);
}

/* Welcome Screen */
.welcome-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    text-align: center;
    animation: fadeIn 1s ease-out;
}

.welcome-icon {
    font-size: 6rem;
    margin-bottom: 1.5rem;
    animation: sacredFloat 3s ease-in-out infinite, fadeIn 1s ease-out;
}

@keyframes sacredFloat {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    25% { transform: translateY(-15px) rotate(5deg); }
    50% { transform: translateY(0) rotate(0deg); }
    75% { transform: translateY(15px) rotate(-5deg); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.welcome-text {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.2rem;
    color: rgba(255, 255, 255, 0.75);
    max-width: 650px;
    line-height: 1.7;
    font-weight: 400;
}

/* Typing Animation */
.typing-indicator {
    display: inline-flex;
    gap: 5px;
    padding: 1rem 1.5rem;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 22px;
    border-bottom-left-radius: 5px;
}

.typing-dot {
    width: 8px;
    height: 8px;
    background: rgba(212, 175, 55, 0.6);
    border-radius: 50%;
    animation: typingBounce 1.4s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-8px); }
}

/* Sidebar */
.sidebar-section {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(212, 175, 55, 0.08);
}

.sidebar-title {
    color: #D4AF37;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.session-item {
    padding: 0.9rem;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 12px;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid transparent;
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.9rem;
}

.session-item:hover {
    background: rgba(255, 107, 53, 0.1);
    border-color: rgba(255, 107, 53, 0.3);
    transform: translateX(5px);
    color: white;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.15);
}

::-webkit-scrollbar-thumb {
    background: rgba(212, 175, 55, 0.25);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(212, 175, 55, 0.4);
}

/* Success/Error Messages */
.stSuccess, .stError {
    border-radius: 12px !important;
    padding: 1rem !important;
    animation: shake 0.5s ease-out;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

/* Spinner */
.stSpinner > div > div {
    border-color: #D4AF37 transparent #D4AF37 transparent !important;
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}

/* Glow Effects */
.glow-gold {
    box-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
}

.glow-orange {
    box-shadow: 0 0 30px rgba(255, 107, 53, 0.3);
}

/* Decorative Lines */
.decorative-line {
    width: 100px;
    height: 2px;
    background: linear-gradient(90deg, transparent, #D4AF37, transparent);
    margin: 1rem auto;
    animation: lineGlow 2s ease-in-out infinite;
}

@keyframes lineGlow {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}

/* Responsive */
@media (max-width: 768px) {
    .main-title { font-size: 2.8rem; }
    .main-subtitle { font-size: 1.1rem; letter-spacing: 3px; }
    .auth-container { padding: 1.5rem; margin: 1rem; }
    .message-bubble { max-width: 88%; }
    .welcome-text { font-size: 1.6rem; }
    .chat-container { padding: 1rem; }
}
</style>

<!-- Floating Om Symbols -->
<div class="floating-elements">
    <span class="floating-om">🕉️</span>
    <span class="floating-om">🕉️</span>
    <span class="floating-om">🕉️</span>
    <span class="floating-om">🕉️</span>
    <span class="floating-om">🕉️</span>
    <span class="floating-om">🕉️</span>
    <span class="floating-om">🕉️</span>
    <span class="floating-om">🕉️</span>
    <span class="floating-om">🕉️</span>
    <span class="floating-om">🕉️</span>
</div>
""",
    unsafe_allow_html=True,
)


def make_authenticated_request(method, endpoint, data=None, files=None):
    if not st.session_state.get("access_token"):
        return None

    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

    try:
        if method == "GET":
            response = requests.get(
                f"{API_BASE_URL}{endpoint}", headers=headers, timeout=30
            )
        elif method == "POST":
            if files:
                response = requests.post(
                    f"{API_BASE_URL}{endpoint}",
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=60,
                )
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(
                    f"{API_BASE_URL}{endpoint}", headers=headers, json=data, timeout=60
                )
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(
                f"{API_BASE_URL}{endpoint}", headers=headers, json=data, timeout=30
            )
        elif method == "DELETE":
            response = requests.delete(
                f"{API_BASE_URL}{endpoint}", headers=headers, timeout=30
            )

        response.raise_for_status()
        return response

    except requests.exceptions.HTTPError as e:
        if e.response and e.response.status_code == 401:
            st.error("🕉️ Your spiritual journey has paused. Please login again.")
            cookies["access_token"] = ""
            cookies.save()
            st.session_state.clear()
            st.rerun()
        else:
            error_msg = (
                e.response.json().get("detail", str(e)) if e.response else str(e)
            )
            st.error(f"✨ Divine interruption: {error_msg}")
    except requests.exceptions.RequestException as e:
        st.error(f"🌅 Connection to the divine realm failed: {str(e)[:50]}")

    return None


def login_page():
    st.markdown('<div class="animated-bg"></div>', unsafe_allow_html=True)

    st.markdown(
        """
    <div class="title-container">
        <h1 class="main-title">🕉️ The Monk AI</h1>
        <div class="decorative-line"></div>
        <p class="main-subtitle">Divine Wisdom From Ancient Scriptures</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.container():
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)

            tab = st.selectbox(
                "",
                ["Login", "Register"],
                label_visibility="collapsed",
                help="Choose Login or Register",
            )

            if tab == "Login":
                with st.form("login_form", clear_on_submit=False):
                    email = st.text_input(
                        "",
                        placeholder="📧 Your Email Address",
                        key="login_email",
                        label_visibility="collapsed",
                    )
                    password = st.text_input(
                        "",
                        placeholder="🔐 Your Password",
                        type="password",
                        key="login_password",
                        label_visibility="collapsed",
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    login_button = st.form_submit_button(
                        "🕉️ Begin Your Journey", use_container_width=True
                    )

                    if login_button:
                        if not email or not password:
                            st.error(
                                "✦ Please enter both email and password to continue"
                            )
                        else:
                            with st.spinner("✨ Opening the gates of wisdom..."):
                                try:
                                    response = requests.post(
                                        f"{API_BASE_URL}/auth/login",
                                        json={"email": email, "password": password},
                                        timeout=15,
                                    )

                                    if response.status_code == 200:
                                        data = response.json()
                                        token = data["access_token"]
                                        st.session_state.access_token = token
                                        st.session_state.logged_in = True

                                        cookies["access_token"] = token
                                        cookies.save()

                                        user_response = make_authenticated_request(
                                            "GET", "/auth/me"
                                        )
                                        if (
                                            user_response
                                            and user_response.status_code == 200
                                        ):
                                            st.session_state.user_info = (
                                                user_response.json()
                                            )
                                            st.session_state.user_mode = (
                                                st.session_state.user_info.get(
                                                    "preferred_mode", "beginner"
                                                )
                                            )

                                        st.success("🙏 Welcome back, seeker!")
                                        time.sleep(1.2)
                                        st.rerun()
                                    else:
                                        st.error(
                                            f"✦ {response.json().get('detail', 'Invalid credentials')}"
                                        )
                                except Exception as e:
                                    st.error(
                                        f"🌅 The universe is not responding: {str(e)[:60]}"
                                    )

            else:
                with st.form("register_form", clear_on_submit=False):
                    full_name = st.text_input(
                        "",
                        placeholder="👤 Your Divine Name",
                        key="register_name",
                        label_visibility="collapsed",
                    )
                    email = st.text_input(
                        "",
                        placeholder="📧 Your Email Address",
                        key="register_email",
                        label_visibility="collapsed",
                    )
                    password = st.text_input(
                        "",
                        placeholder="🔐 Create Password",
                        type="password",
                        key="register_password",
                        label_visibility="collapsed",
                    )
                    confirm_password = st.text_input(
                        "",
                        placeholder="🔐 Confirm Password",
                        type="password",
                        key="register_confirm_password",
                        label_visibility="collapsed",
                    )
                    preferred_mode = st.selectbox(
                        "",
                        ["beginner", "expert"],
                        format_func=lambda x: (
                            "🌱 Beginner - Guided Learning"
                            if x == "beginner"
                            else "🧠 Expert - Deep Insights"
                        ),
                        key="register_mode",
                        label_visibility="collapsed",
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    register_button = st.form_submit_button(
                        "🕉️ Begin Your Journey", use_container_width=True
                    )

                    if register_button:
                        if not full_name or not email or not password:
                            st.error("✦ Please fill all the sacred fields")
                        elif password != confirm_password:
                            st.error("✦ The passwords do not align with the universe")
                        elif len(password) < 6:
                            st.error(
                                "✦ Password must be at least 6 characters for protection"
                            )
                        else:
                            try:
                                response = requests.post(
                                    f"{API_BASE_URL}/auth/register",
                                    json={
                                        "email": email,
                                        "password": password,
                                        "full_name": full_name,
                                        "preferred_mode": preferred_mode,
                                    },
                                    timeout=15,
                                )

                                if response.status_code == 200:
                                    st.success(
                                        "🎉 Your spiritual journey begins! Please login."
                                    )
                                else:
                                    st.error(
                                        f"✦ {response.json().get('detail', 'Registration failed')}"
                                    )
                            except Exception as e:
                                st.error(
                                    f"🌅 The universe blocked your path: {str(e)[:60]}"
                                )

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
    <div style="text-align: center; margin-top: 2.5rem; color: rgba(255,255,255,0.35); font-size: 0.85rem;">
        <p>✦ Powered by <span style="color: #D4AF37;">Endee Vector Database</span> ✦ Groq AI ✦</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def chat_interface():
    with st.container():
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(
                """
            <div class="chat-title">🕉️ The Monk AI</div>
            """,
                unsafe_allow_html=True,
            )
        with col2:
            mode = st.selectbox(
                "",
                ["beginner", "expert"],
                index=0 if st.session_state.user_mode == "beginner" else 1,
                format_func=lambda x: "🌱" if x == "beginner" else "🧠",
                key="mode_select",
                label_visibility="collapsed",
            )
            st.session_state.user_mode = mode

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown(
            """
        <div class="welcome-screen">
            <div class="welcome-icon">🕉️</div>
            <div class="welcome-text">
                🙏 Namaste, Seeker!<br><br>
                ✦ Ask me anything about Hindu scriptures,<br>
                philosophy, dharma, karma, or spiritual wisdom...
            </div>
            <div class="decorative-line"></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    display_chat_history()
    st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                user_input = st.text_area(
                    "",
                    placeholder="💭 What wisdom do you seek?...",
                    key="user_input",
                    label_visibility="collapsed",
                    height=55,
                )
            with col2:
                submit = st.form_submit_button("🕉️", use_container_width=True)

        if submit and user_input.strip():
            process_query(user_input)

        st.markdown("</div>", unsafe_allow_html=True)


def process_query(input_data):
    st.session_state.chat_history.append(
        {"role": "user", "content": input_data, "timestamp": datetime.now().isoformat()}
    )

    data = {
        "query": input_data,
        "mode": st.session_state.user_mode,
        "session_id": st.session_state.current_session_id,
    }

    with st.spinner("🔮 Consulting the ancient texts..."):
        response = make_authenticated_request("POST", "/chat/query", data=data)

    if response and response.status_code == 200:
        result = response.json()
        st.session_state.current_session_id = result["session_id"]

        assistant_message = {
            "role": "assistant",
            "content": result["answer"],
            "hindi_translation": result["hindi_translation"],
            "citations": result["citations"],
            "recommendations": result["recommendations"],
            "keywords_explained": result.get("keywords_explained"),
            "timestamp": datetime.now().isoformat(),
        }
        st.session_state.chat_history.append(assistant_message)
        st.rerun()
    else:
        if response is not None:
            st.session_state.chat_history.pop()
            st.error("The ancient texts could not provide an answer. Please try again.")
            st.rerun()


def display_chat_history():
    for idx, message in enumerate(st.session_state.chat_history):
        role = message.get("role")

        if role == "user":
            st.markdown(
                f"""
            <div class="message-wrapper user" style="animation-delay: 0.1s;">
                <div class="message-bubble user-message">
                    <div class="message-role">You</div>
                    {message["content"]}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        elif role == "assistant":
            st.markdown(
                f"""
            <div class="message-wrapper assistant" style="animation-delay: 0.1s;">
                <div class="message-bubble assistant-message">
                    <div class="message-role">🕉️ The Monk AI</div>
                    {message["content"]}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if message.get("hindi_translation"):
                st.markdown(
                    f"""
                <div class="response-section hindi-translation" style="animation-delay: 0.2s;">
                    <div style="color: #7B2CBF; font-weight: 600; margin-bottom: 0.5rem;">🕉️ हिंदी अनुवाद:</div>
                    {message["hindi_translation"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            if message.get("keywords_explained"):
                st.markdown(
                    f"""
                <div class="response-section" style="animation-delay: 0.3s;">
                    <div style="color: #D4AF37; font-weight: 600; margin-bottom: 0.8rem;">📚 Spiritual Terms Explained</div>
                """,
                    unsafe_allow_html=True,
                )
                for term, explanation in message["keywords_explained"].items():
                    st.markdown(
                        f"""
                    <div class="keyword-card">
                        <span style="color: #FF6B35; font-weight: 600;">{term.title()}:</span> {explanation}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            if message.get("citations"):
                st.markdown(
                    f"""
                <div class="response-section" style="animation-delay: 0.4s;">
                    <div style="color: #D4AF37; font-weight: 600; margin-bottom: 0.8rem;">📖 Sacred Sources</div>
                """,
                    unsafe_allow_html=True,
                )
                for i, citation in enumerate(message["citations"], 1):
                    st.markdown(
                        f"""
                    <div class="citation-card">
                        <div class="citation-book">{i}. {citation["book"]}</div>
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin-top: 0.3rem;">
                            {citation.get("chapter", "")} {citation.get("section", "")} {citation.get("verse", "")}
                        </div>
                        <div style="color: rgba(255,255,255,0.4); font-style: italic; margin-top: 0.5rem; font-size: 0.8rem;">
                            "{citation.get("content_preview", "")}"
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            if message.get("recommendations"):
                recs = " • ".join([f"📜 {book}" for book in message["recommendations"]])
                st.markdown(
                    f"""
                <div class="recommendation-card" style="animation-delay: 0.5s;">
                    <div style="color: #4CAF50; font-weight: 600; margin-bottom: 0.8rem;">📚 Recommended for Deeper Study</div>
                    <div>{recs}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )


def sidebar_content():
    with st.container():
        st.markdown(
            f"""
        <div class="sidebar-section" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🕉️</div>
            <div style="color: #D4AF37; font-weight: 600; font-size: 1.1rem;">
                🙏 {st.session_state.user_info.get("full_name", "Seeker")}
            </div>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem; margin-top: 0.3rem;">
                {"🌱 Beginner" if st.session_state.user_mode == "beginner" else "🧠 Expert"} Mode
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚪 Leave Temple", use_container_width=True):
            cookies["access_token"] = ""
            cookies.save()
            st.session_state.clear()
            st.rerun()

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-title">🕉️ Past Journeys</div>', unsafe_allow_html=True
    )

    try:
        response = make_authenticated_request("GET", "/chat/sessions")
        if response and response.status_code == 200:
            sessions = response.json()
            if sessions:
                for session in sessions[:10]:
                    session_title = (
                        session["title"][:35] + "..."
                        if len(session["title"]) > 35
                        else session["title"]
                    )
                    if st.button(
                        f"💭 {session_title}",
                        key=f"session_{session['session_id']}",
                        use_container_width=True,
                    ):
                        load_chat_session(session["session_id"])
            else:
                st.info("No past journeys yet")
    except Exception as e:
        st.error("Could not load past journeys")


def load_chat_session(session_id):
    try:
        response = make_authenticated_request("GET", f"/chat/sessions/{session_id}")
        if response and response.status_code == 200:
            session_data = response.json()
            st.session_state.current_session_id = session_id
            st.session_state.chat_history = session_data.get("messages", [])
            st.rerun()
    except Exception as e:
        st.error(f"Could not retrieve that journey: {str(e)}")


def restore_session_from_cookie():
    token = cookies.get("access_token")
    if not token:
        return False

    st.session_state.access_token = token
    user_response = make_authenticated_request("GET", "/auth/me")

    if user_response and user_response.status_code == 200:
        st.session_state.user_info = user_response.json()
        st.session_state.user_mode = st.session_state.user_info.get(
            "preferred_mode", "beginner"
        )
        st.session_state.logged_in = True
        return True

    return False


def main():
    if st.session_state.get("logged_in"):
        col1, col2 = st.columns([4, 1])
        with col1:
            pass
        with col2:
            sidebar_content()
        chat_interface()
    elif restore_session_from_cookie():
        st.rerun()
    else:
        login_page()


if __name__ == "__main__":
    main()
