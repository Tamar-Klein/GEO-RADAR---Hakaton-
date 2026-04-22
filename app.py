import streamlit as st
import os
from utils.ai_engine import run_chat_audit, FIXED_QUESTIONS
from utils.analysts import analyze_gap, company, competitors
from components.style import apply_custom_css
from components.ui_utils import load_sidebar, load_top_bar

# ============== הגדרות דף חובה (חייב להיות ראשון) ==============
st.set_page_config(
    page_title="GEO RADAR – ביטוח ישיר",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== אתחול זיכרון (Session State) ==============
if 'audit_results' not in st.session_state:
    st.session_state.audit_results = []
if 'baseline_snapshot' not in st.session_state:
    st.session_state.baseline_snapshot = None
if 'scan_phase' not in st.session_state:
    st.session_state.scan_phase = 'hero'

# ============== החלת עיצוב ותפריטים ==============
apply_custom_css()
load_sidebar()
load_top_bar()

# ============== לוגיקת ניתוב ==============
has_data = bool(st.session_state.audit_results)

# כותרת הדף המשתנה
header_text = "AI Visibility Snapshot" if has_data else "GEO Radar – סריקת נוכחות AI"
st.markdown(f'<div class="page-title">{header_text}</div>', unsafe_allow_html=True)

if has_data and st.session_state.scan_phase == 'done':
    st.switch_page("pages/1_Dashboard.py")

# ============== מסכי טרום-סריקה (Hero / Chat) ==============
if not has_data:
    phase = st.session_state.scan_phase

    # --- מסך פתיחה (Hero) ---
    if phase == 'hero':
        st.markdown(f"""
        <div class="hero-card">
            <div class="hero-icon">📡</div>
            <div class="hero-title">GEO Radar</div>
            <div class="hero-sub">ננתח איך <b>ChatGPT</b>, <b>Gemini</b> ו-<b>Claude</b> עונים על שאלות ביטוח נפוצות, נזהה מאיפה ה-AI שואב מידע, ונגלה מתי <b>ביטוח ישיר</b> מוזכר — ומתי לא.</div>
            <div class="hero-stats">
                <div class="hero-stat"><div class="hero-stat-num">{len(FIXED_QUESTIONS)}</div><div class="hero-stat-lbl">שאילתות</div></div>
                <div class="hero-stat"><div class="hero-stat-num">3</div><div class="hero-stat-lbl">מודלי AI</div></div>
                <div class="hero-stat"><div class="hero-stat-num">Live</div><div class="hero-stat-lbl">ציטוטים חיים</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="hero-btn-wrap">', unsafe_allow_html=True)
        cL, cM, cR = st.columns([2, 1, 2])
        with cM:
            if st.button("🚀 התחל סריקה", use_container_width=True):
                st.session_state.scan_phase = 'chat'
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # --- מסך סריקה פעילה (Chat) ---
    elif phase == 'chat':
        chat_ph = st.empty()
        run_chat_audit(chat_ph)
        
        # סיום הסריקה ומעבר לדשבורד
        st.session_state.scan_phase = 'done'
        st.rerun()