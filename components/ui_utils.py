import streamlit as st
import os
import re
import base64

# --- בועות צ'אט ועיצוב טקסט AI ---

def _bubble_user(q):
    """יצירת בועת משתמש לשלב הסריקה"""
    return f'<div class="bubble-row bubble-row-user"><div class="bubble-user">{q}</div></div>'

def _bubble_ai_typing():
    """יצירת אנימציית טעינה (שלוש נקודות) של ה-AI"""
    return '<div class="bubble-row bubble-row-ai"><div class="bubble-ai"><div class="typing"><span></span><span></span><span></span></div></div></div>'

def _bubble_ai_done(n_sources, domains):
    """יצירת בועת סיום שאילתה עם פירוט מקורות"""
    tags = "".join(f'<span class="src-tag">{d}</span>' for d in domains[:3])
    return (f'<div class="bubble-row bubble-row-ai"><div class="bubble-ai">'
            f'✅ קיבלתי תשובות מ-<b>ChatGPT</b>, <b>Gemini</b> ו-<b>Claude</b> · חולצו <b>{n_sources}</b> מקורות<br>'
            f'<div style="margin-top:6px">{tags}</div></div></div>')

def format_ai_text(text):
    """המרת Markdown links לקישורי HTML יפים + הסתרת URLs חשופים ארוכים"""
    if not text:
        return ""
    # [text](url) -> <a href="url" target="_blank">text</a>
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        lambda m: f'<a href="{m.group(2)}" target="_blank" class="ai-link">{m.group(1)}</a>',
        text
    )
    # URLs חשופים ארוכים -> קישור עם דומיין בלבד
    def _short_url(m):
        url = m.group(0)
        dom = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
        return f'<a href="{url}" target="_blank" class="ai-link">{dom}</a>'
    text = re.sub(r'https?://[^\s<)"]+', _short_url, text)
    # **bold** -> <b>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    # newlines
    text = text.replace('\n', '<br>')
    return text

# --- ניווט ולוגו ---

def _load_logo():
    """טעינת לוגו מקובץ מקומי או החזרת SVG חלופי של ביטוח ישיר"""
    for ext in ('png', 'jpg', 'jpeg', 'svg'):
        p = f"logo.{ext}"
        if os.path.exists(p):
            mime = 'image/svg+xml' if ext == 'svg' else f'image/{ext if ext != "jpg" else "jpeg"}'
            with open(p, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode()
            return f'<img src="data:{mime};base64,{b64}" style="max-width:100%;height:auto;display:block;">'
    
    # fallback SVG של ביטוח ישיר במידה ואין קובץ לוגו
    return ('<div class="idi-logo-row">'
            '<div class="idi-logo-text">'
            '<div class="idi-logo-top">ביטוח</div>'
            '<div class="idi-logo-bottom">ישיר</div>'
            '<div class="idi-logo-tag">IDI חברה לביטוח בע״מ</div>'
            '</div>'
            '<div class="idi-logo-dots">'
            '<svg width="56" height="40" viewBox="0 0 56 40">'
            '<circle cx="8" cy="8" r="6" fill="#ED1F4A"/>'
            '<circle cx="28" cy="8" r="6" fill="#ED1F4A"/>'
            '<circle cx="48" cy="8" r="6" fill="#ED1F4A"/>'
            '<circle cx="28" cy="28" r="6" fill="#ED1F4A"/>'
            '<circle cx="48" cy="28" r="6" fill="#ED1F4A"/>'
            '</svg></div></div>')

def load_sidebar():
    """טעינת ה-Sidebar המעוצב לכל עמודי האפליקציה"""
    with st.sidebar:
        st.markdown(f'<div class="idi-logo-wrap">{_load_logo()}</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="side-section-title">Dashboards</div>
        <div class="side-nav-item active"><span class="side-nav-icon">⌂</span> סקירה כללית</div>
        <div class="side-nav-item"><span class="side-nav-icon">📈</span> ניתוח פערים</div>
        <div class="side-nav-item"><span class="side-nav-icon">🗺️</span> מפת מקורות AI</div>
        <div class="side-nav-item"><span class="side-nav-icon">🤖</span> סוכן RAG</div>
        <div class="side-footer">❋ snowUI</div>
        """, unsafe_allow_html=True)

def load_top_bar():
    """טעינת ה-Top Bar המעוצב לכל עמודי האפליקציה"""
    st.markdown("""
    <div class="top-bar">
        <div class="top-bar-left">
            <span>☰</span>
            <span>★</span>
            <span>Dashboards</span>
            <span class="top-bar-sep">/</span>
            <span class="top-bar-crumb-active">Default</span>
        </div>
        <div class="top-search">
            <span>🔍 Search</span>
            <span>⌘/</span>
        </div>
        <div class="top-bar-icons">
            <span>☀️</span><span>↻</span><span>🔔</span><span>☰</span>
        </div>
    </div>
    """, unsafe_allow_html=True)