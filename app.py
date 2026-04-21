import os
import re
import ssl
import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import Counter
from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai
from google.genai import types as genai_types
from openai import OpenAI
import httpx

# Anthropic (Claude) - optional; works when anthropic package is installed + key exists
try:
    from anthropic import Anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    Anthropic = None
    _ANTHROPIC_AVAILABLE = False

# --- SSL ---
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()

st.set_page_config(page_title="GEO RADAR – ביטוח ישיר", page_icon="📡", layout="wide")

# ============== CSS - Clean Dashboard (IDI style) ==============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Assistant', sans-serif !important; }
.stApp { background-color: #f5f6fa; direction: rtl; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ======= SIDEBAR ======= */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-left: 1px solid #eef0f4;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

.idi-logo-wrap {
    padding: 22px 18px 18px 18px;
    border-bottom: 1px solid #f0f1f5;
    margin-bottom: 14px;
}
.idi-logo-row {
    display: flex;
    flex-direction: row-reverse;
    align-items: center;
    justify-content: flex-start;
    gap: 12px;
}
.idi-logo-text { text-align: right; }
.idi-logo-top {
    font-family: 'Assistant', sans-serif;
    font-weight: 800;
    font-size: 26px;
    line-height: 1;
    color: #0a1a3a;
    letter-spacing: -0.5px;
}
.idi-logo-bottom {
    font-weight: 800;
    font-size: 26px;
    line-height: 1;
    color: #0a1a3a;
    margin-top: 2px;
}
.idi-logo-dots { display: inline-flex; align-items: center; }
.idi-logo-tag {
    color: #9aa3b2;
    font-size: 9.5px;
    margin-top: 4px;
    letter-spacing: 0.3px;
    font-weight: 500;
}

.side-section-title {
    color: #9aa3b2;
    font-size: 12px;
    font-weight: 600;
    padding: 8px 22px 6px 22px;
    letter-spacing: 0.3px;
}
.side-nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 22px;
    color: #4b5563;
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
    border-right: 3px solid transparent;
    transition: all .15s;
}
.side-nav-item:hover { background: #f8f9fc; color: #0a1a3a; }
.side-nav-item.active {
    background: #f5f6fa;
    color: #0a1a3a;
    border-right-color: #ED1F4A;
    font-weight: 700;
}
.side-nav-icon { font-size: 17px; width: 20px; text-align: center; }

.side-footer {
    position: absolute;
    bottom: 16px;
    right: 22px;
    color: #c2c7d0;
    font-size: 12px;
    font-weight: 600;
}
.side-footer .dot { color: #ED1F4A; font-size: 14px; margin-left: 4px; }

/* ======= TOP BAR ======= */
.top-bar {
    background: white;
    border: 1px solid #eef0f4;
    border-radius: 14px;
    padding: 10px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 22px;
    box-shadow: 0 1px 2px rgba(16,24,40,.04);
}
.top-bar-left { display: flex; align-items: center; gap: 14px; color: #6b7280; font-size: 14px; font-weight: 500; }
.top-bar-sep { color: #d1d5db; }
.top-bar-crumb-active { color: #0a1a3a; font-weight: 700; }
.top-bar-icons { display: flex; gap: 14px; align-items: center; color: #9aa3b2; font-size: 16px; }
.top-search {
    background: #f5f6fa;
    border: 1px solid #eef0f4;
    border-radius: 8px;
    padding: 6px 14px;
    color: #9aa3b2;
    font-size: 13px;
    min-width: 260px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* ======= PAGE TITLE ======= */
.page-title { font-size: 26px; font-weight: 800; color: #0a1a3a; margin: 6px 0 22px 0; }

/* ======= DASHBOARD CARDS ======= */
.dash-card {
    background: white;
    border-radius: 18px;
    padding: 24px 28px;
    box-shadow: 0 1px 2px rgba(16,24,40,.04), 0 4px 16px rgba(16,24,40,.04);
    border: 1px solid #f0f1f5;
    margin-bottom: 22px;
}
.card-title { font-size: 18px; font-weight: 700; color: #0a1a3a; margin-bottom: 6px; }
.card-title .crit { color: #ED1F4A; font-weight: 800; }
.card-subtitle { font-size: 13px; color: #9aa3b2; margin-bottom: 14px; }

/* ======= GAUGE ======= */
.gauge-value {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    color: #0a1a3a;
    margin-top: -60px;
    position: relative;
    z-index: 2;
}
.gauge-label { text-align: center; color: #6b7280; font-size: 14px; margin-top: 8px; }

/* ======= LIVE FEED TABLE ======= */
.feed-wrap { background: white; border-radius: 18px; padding: 24px 28px; border: 1px solid #f0f1f5; box-shadow: 0 1px 2px rgba(16,24,40,.04), 0 4px 16px rgba(16,24,40,.04); }
.feed-title { font-size: 15px; color: #9aa3b2; font-weight: 600; margin-bottom: 16px; }
table.feed {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}
table.feed thead th {
    text-align: right;
    color: #9aa3b2;
    font-weight: 500;
    padding: 10px 14px;
    border-bottom: 1px solid #f0f1f5;
    font-size: 13px;
}
table.feed tbody td {
    padding: 14px;
    border-bottom: 1px solid #f5f6fa;
    color: #374151;
    vertical-align: middle;
}
.src-cell { display: flex; align-items: center; gap: 10px; font-weight: 600; color: #0a1a3a; }
.src-avatar { width: 28px; height: 28px; border-radius: 50%; background: #e5e7eb; display: inline-flex; align-items: center; justify-content: center; font-size: 13px; color: #6b7280; font-weight: 700; }
.pill-red { color: #ED1F4A; font-weight: 700; }
.pill-green { color: #16a34a; font-weight: 700; }
.insight { display: inline-flex; align-items: center; gap: 6px; font-weight: 600; font-size: 13px; }
.insight::before { content: '●'; font-size: 10px; }
.insight.prog { color: #2563eb; }
.insight.comp { color: #16a34a; }
.insight.pend { color: #7c3aed; }
.insight.appr { color: #ca8a04; }

/* feed - cited by tags */
.feed-by {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 999px;
    font-size: 12px; font-weight: 700;
}
.feed-by-gem  { background: #fce7f3; color: #be185d; }
.feed-by-chat { background: #dbeafe; color: #1e40af; }
.feed-by-both { background: linear-gradient(90deg,#fce7f3,#dbeafe); color: #581c87; }
.feed-by-claude { background: #fef3c7; color: #b45309; }
.feed-by-all { background: linear-gradient(90deg,#fce7f3,#dbeafe,#fef3c7); color: #7c2d12; font-weight: 800; }

/* feed - frequency bar */
.feed-freq { display: flex; align-items: center; gap: 8px; min-width: 120px; }
.feed-freq-bar {
    flex: 1; height: 6px; background: #f0f1f5;
    border-radius: 999px; overflow: hidden;
}
.feed-freq-fill {
    height: 100%;
    background: linear-gradient(90deg, #ED1F4A, #ff6b8a);
    border-radius: 999px;
}
.feed-freq-txt {
    font-size: 12px; color: #6b7280; font-weight: 700;
    min-width: 32px; text-align: center;
}

/* feed - action cells */
.feed-action-hot { color: #991b1b; font-weight: 700; }
.feed-action-ok  { color: #166534; font-weight: 600; }
.feed-action-mid { color: #6b7280; font-weight: 500; }

/* ======= QUESTION CARDS (detailed results) ======= */
.q-card {
    background: white;
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 18px;
    border: 1px solid #f0f1f5;
    box-shadow: 0 1px 2px rgba(16,24,40,.04);
}
.q-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 14px;
    border-bottom: 1px solid #f0f1f5;
    margin-bottom: 18px;
}
.q-title { font-size: 17px; font-weight: 700; color: #0a1a3a; }
.q-badges { display: flex; gap: 6px; flex-wrap: wrap; }
.q-badge { font-size: 12px; padding: 4px 10px; border-radius: 12px; font-weight: 600; }
.q-badge-us-in { background: #dcfce7; color: #166534; }
.q-badge-us-out { background: #fee2e2; color: #991b1b; }
.q-badge-score { background: #eef0f4; color: #374151; }
.q-badge-comp { background: #fff0f3; color: #ED1F4A; border: 1px solid #ffd1dc; }

.ans-box {
    border: 1px solid #eef0f4;
    border-radius: 14px;
    padding: 16px 18px;
    background: #fbfbfd;
    font-size: 14px;
    line-height: 1.85;
    color: #1f2937;
    min-height: 150px;
    direction: rtl;
    text-align: right;
    unicode-bidi: plaintext;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
.ans-box * { direction: rtl; text-align: right; unicode-bidi: plaintext; }
.ans-head {
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eef0f4;
}
.ans-head-chat { color: #0a1a3a; }
.ans-head-gem  { color: #ED1F4A; }

.sources-title { font-size: 13px; color: #9aa3b2; font-weight: 600; margin: 16px 0 10px 0; }
.src-pill {
    display: inline-block;
    background: #f5f6fa;
    border: 1px solid #eef0f4;
    border-radius: 999px;
    padding: 6px 14px;
    margin: 4px 4px 4px 0;
    font-size: 12.5px;
    color: #374151;
    text-decoration: none;
    transition: all .15s;
}
.src-pill:hover { background: #0a1a3a; color: white !important; }
.src-pill-us { background: #fff0f3; border-color: #ffd1dc; color: #ED1F4A; font-weight: 700; }

.rec-box {
    background: #fff8e7;
    border-right: 3px solid #eab308;
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 14px;
    font-size: 13.5px;
    color: #713f12;
    line-height: 1.6;
}
.rec-box-ok { background: #ecfdf5; border-right-color: #16a34a; color: #166534; }

/* ======= HERO (landing) ======= */
.hero-card {
    background: white;
    border-radius: 22px;
    padding: 70px 40px 60px 40px;
    border: 1px solid #f0f1f5;
    box-shadow: 0 1px 2px rgba(16,24,40,.04), 0 8px 28px rgba(16,24,40,.06);
    text-align: center;
    margin: 40px auto;
    max-width: 720px;
}
.hero-icon { font-size: 56px; margin-bottom: 10px; }
.hero-title { font-size: 32px; font-weight: 800; color: #0a1a3a; margin-bottom: 10px; letter-spacing: -0.5px; }
.hero-sub { color: #6b7280; font-size: 16px; line-height: 1.7; max-width: 520px; margin: 0 auto 32px auto; }
.hero-stats { display: flex; justify-content: center; gap: 28px; margin-bottom: 32px; flex-wrap: wrap; }
.hero-stat { background: #fbfbfd; border: 1px solid #eef0f4; border-radius: 12px; padding: 14px 22px; min-width: 110px; }
.hero-stat-num { font-size: 22px; font-weight: 800; color: #ED1F4A; }
.hero-stat-lbl { color: #6b7280; font-size: 12px; font-weight: 600; margin-top: 2px; }

/* Center the big run button */
.hero-btn-wrap { text-align: center; }
.hero-btn-wrap .stButton > button {
    font-size: 18px !important;
    padding: 16px 48px !important;
    border-radius: 999px !important;
    box-shadow: 0 6px 20px rgba(237,31,74,.35) !important;
}

/* ======= CHAT ======= */
.chat-wrap {
    max-width: 780px;
    margin: 0 auto;
    background: white;
    border: 1px solid #f0f1f5;
    border-radius: 18px;
    padding: 28px 26px;
    box-shadow: 0 1px 2px rgba(16,24,40,.04), 0 4px 16px rgba(16,24,40,.04);
    min-height: 420px;
}
.chat-header {
    padding-bottom: 14px;
    border-bottom: 1px solid #f0f1f5;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.chat-avatar {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #0a1a3a, #ED1F4A);
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 16px;
}
.chat-head-txt { flex: 1; }
.chat-head-name { font-weight: 700; color: #0a1a3a; font-size: 15px; }
.chat-head-status { font-size: 12px; color: #16a34a; display: flex; align-items: center; gap: 4px; }
.chat-head-status::before { content: '●'; font-size: 9px; }

.bubble-row { display: flex; margin: 10px 0; direction: rtl; }
.bubble-row-user { justify-content: flex-start; }
.bubble-row-ai { justify-content: flex-end; }
.bubble-user {
    background: #ED1F4A; color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    max-width: 72%;
    font-size: 15px;
    line-height: 1.5;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(237,31,74,.2);
    animation: slide-in-r .35s ease;
}
.bubble-ai {
    background: #f5f6fa; color: #1f2937;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    max-width: 72%;
    font-size: 14px;
    line-height: 1.6;
    border: 1px solid #eef0f4;
    animation: slide-in-l .35s ease;
}
.bubble-ai .src-tag {
    display: inline-block; background: white; border: 1px solid #e5e7eb;
    padding: 3px 10px; border-radius: 10px; font-size: 11.5px;
    margin: 4px 4px 0 0; color: #6b7280;
}
.typing { display: inline-flex; gap: 4px; padding: 6px 0; }
.typing span {
    width: 7px; height: 7px; background: #9aa3b2; border-radius: 50%;
    animation: bounce 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: .15s; }
.typing span:nth-child(3) { animation-delay: .3s; }
@keyframes bounce { 0%,60%,100%{transform:translateY(0);opacity:.5} 30%{transform:translateY(-5px);opacity:1} }
@keyframes slide-in-r { from { opacity:0; transform:translateX(-20px) } to { opacity:1; transform:translateX(0) } }
@keyframes slide-in-l { from { opacity:0; transform:translateX(20px) } to { opacity:1; transform:translateX(0) } }

/* ======= PREMIUM DETAILED QUESTION CARDS ======= */
.qx-wrap { margin-bottom: 32px; animation: fadeUp .5s ease; }
@keyframes fadeUp { from { opacity:0; transform:translateY(15px) } to { opacity:1; transform:translateY(0) } }

.qx-card {
    background: white;
    border-radius: 24px;
    border: 1px solid #f0f1f5;
    box-shadow: 0 1px 2px rgba(16,24,40,.04), 0 10px 30px rgba(16,24,40,.06);
    overflow: hidden;
    position: relative;
}

/* Top gradient strip */
.qx-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #ED1F4A, #0a1a3a);
}

.qx-header {
    display: flex; align-items: center; gap: 20px;
    padding: 26px 30px 20px 30px;
    border-bottom: 1px solid #f5f6fa;
}
.qx-index {
    flex-shrink: 0;
    width: 56px; height: 56px;
    border-radius: 16px;
    background: linear-gradient(135deg, #ED1F4A, #c91a3e);
    color: white;
    font-size: 22px; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 6px 16px rgba(237,31,74,.3);
}
.qx-header-body { flex: 1; min-width: 0; }
.qx-question {
    font-size: 19px; font-weight: 800; color: #0a1a3a;
    margin-bottom: 8px; line-height: 1.4;
}
.qx-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.qx-tag {
    font-size: 12px; padding: 4px 11px; border-radius: 999px;
    font-weight: 700; display: inline-flex; align-items: center; gap: 5px;
}
.qx-tag-in    { background: #dcfce7; color: #14532d; }
.qx-tag-out   { background: #fee2e2; color: #7f1d1d; }
.qx-tag-score { background: #eef0f4; color: #374151; }
.qx-tag-comp  { background: #fff0f3; color: #be185d; border: 1px solid #fbcfe8; }

/* Score ring (circular progress) */
.qx-score-ring {
    flex-shrink: 0;
    width: 74px; height: 74px;
    position: relative;
}
.qx-score-ring svg { transform: rotate(-90deg); }
.qx-score-ring-txt {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    font-weight: 800; color: #0a1a3a;
}
.qx-score-val { font-size: 19px; line-height: 1; }
.qx-score-lbl { font-size: 9px; color: #9aa3b2; margin-top: 2px; letter-spacing: .5px; }

/* Section title inside card */
.qx-section {
    padding: 22px 30px 6px 30px;
    font-size: 12px; font-weight: 700; color: #9aa3b2;
    letter-spacing: 1.2px; text-transform: uppercase;
    display: flex; align-items: center; gap: 8px;
}
.qx-section::before {
    content: ''; width: 28px; height: 2px; background: #ED1F4A; border-radius: 2px;
}

/* AI MODEL CARDS */
.qx-ai-grid { padding: 12px 30px 0 30px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
@media (max-width: 1100px) { .qx-ai-grid { grid-template-columns: 1fr; } }
.qx-ai {
    border-radius: 16px;
    border: 1.5px solid #eef0f4;
    background: #fbfbfd;
    overflow: hidden;
    transition: all .2s;
}
.qx-ai:hover { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(16,24,40,.08); }
.qx-ai-head {
    padding: 12px 18px;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid #eef0f4;
    font-weight: 700; font-size: 14px;
}
.qx-ai-head-left { display: flex; align-items: center; gap: 10px; }
.qx-ai-logo {
    width: 32px; height: 32px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; color: white; font-weight: 800;
}
.qx-ai-chat .qx-ai-head { background: linear-gradient(90deg, #0a1a3a, #1e3a8a); color: white; }
.qx-ai-chat .qx-ai-logo { background: rgba(255,255,255,.22); }
.qx-ai-gem .qx-ai-head  { background: linear-gradient(90deg, #ED1F4A, #c91a3e); color: white; }
.qx-ai-gem  .qx-ai-logo { background: rgba(255,255,255,.22); }
.qx-ai-claude .qx-ai-head { background: linear-gradient(90deg, #d97706, #b45309); color: white; }
.qx-ai-claude .qx-ai-logo { background: rgba(255,255,255,.22); }
.qx-ai-status {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(255,255,255,.18);
    padding: 3px 10px; border-radius: 999px;
    font-size: 11.5px; font-weight: 600;
}
.qx-ai-body {
    padding: 16px 18px;
    font-size: 14px; line-height: 1.85; color: #1f2937;
    direction: rtl; text-align: right; unicode-bidi: plaintext;
    min-height: 130px;
}
.qx-ai-body * { direction: rtl; text-align: right; unicode-bidi: plaintext; }
.qx-ai-body .ai-link,
.ai-link {
    color: #ED1F4A !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    background: #fff5f7;
    padding: 1px 7px;
    border-radius: 6px;
    border: 1px solid #fde2ea;
    white-space: nowrap;
    display: inline-block;
    margin: 0 2px;
    max-width: 240px;
    overflow: hidden;
    text-overflow: ellipsis;
    vertical-align: middle;
    direction: ltr;
}
.qx-ai-body .ai-link:hover,
.ai-link:hover {
    background: #ED1F4A;
    color: white !important;
    border-color: #ED1F4A;
}

/* SOURCE CARDS GRID */
.qx-src-grid {
    padding: 10px 30px 4px 30px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 12px;
}
.qx-src {
    background: #fbfbfd;
    border: 1px solid #eef0f4;
    border-radius: 14px;
    padding: 14px 16px;
    display: flex; gap: 12px; align-items: flex-start;
    text-decoration: none !important;
    transition: all .18s;
    position: relative;
    overflow: hidden;
}
.qx-src:hover {
    transform: translateY(-2px);
    border-color: #0a1a3a;
    box-shadow: 0 8px 20px rgba(10,26,58,.12);
}
.qx-src-us { background: linear-gradient(135deg, #fff5f7, #fff); border-color: #ffb6c8; }
.qx-src-us::before {
    content: '★ ביטוח ישיר'; position: absolute;
    top: 8px; left: 8px;
    background: #ED1F4A; color: white;
    font-size: 10px; font-weight: 700;
    padding: 2px 8px; border-radius: 6px;
}
.qx-src-favicon {
    width: 40px; height: 40px; border-radius: 10px;
    background: white;
    border: 1px solid #eef0f4;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; overflow: hidden;
}
.qx-src-favicon img { width: 26px; height: 26px; }
.qx-src-body { flex: 1; min-width: 0; }
.qx-src-title {
    font-weight: 700; font-size: 13.5px; color: #0a1a3a;
    margin-bottom: 4px; line-height: 1.35;
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
}
.qx-src-meta {
    display: flex; gap: 6px; align-items: center; flex-wrap: wrap;
    font-size: 11px; color: #9aa3b2; font-weight: 600;
}
.qx-src-cat {
    background: #eef0f4; color: #4b5563;
    padding: 2px 7px; border-radius: 6px;
}
.qx-src-auth {
    background: #0a1a3a; color: white;
    padding: 2px 7px; border-radius: 6px;
}
.qx-src-by {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 8px; border-radius: 6px;
    font-size: 10.5px; font-weight: 700;
}
.qx-src-by-gem  { background: #fce7f3; color: #be185d; }
.qx-src-by-chat { background: #dbeafe; color: #1e40af; }
.qx-src-by-both { background: linear-gradient(90deg,#fce7f3,#dbeafe); color: #581c87; }
.qx-src-by-claude { background: #fef3c7; color: #b45309; }
.qx-src-by-all { background: linear-gradient(90deg,#fce7f3,#dbeafe,#fef3c7); color: #7c2d12; font-weight: 800; }

/* CROSS JUDGMENT PANEL — Claude as Universal Judge */
.qx-judge-section {
    margin: 18px 30px 8px 30px;
}
.qx-judge-title {
    display: flex; align-items: center; gap: 10px;
    font-size: 15px; font-weight: 800;
    color: #581c87;
    padding: 10px 16px;
    background: linear-gradient(90deg, #faf5ff, #fdf4ff);
    border-radius: 12px 12px 0 0;
    border: 1.5px solid #e9d5ff;
    border-bottom: none;
}
.qx-judge-badge {
    display: inline-flex; align-items: center; gap: 4px;
    background: #a855f7; color: white;
    padding: 3px 10px; border-radius: 999px;
    font-size: 11px; font-weight: 700;
}
.qx-judge-grid {
    display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;
    padding: 16px;
    background: white;
    border: 1.5px solid #e9d5ff;
    border-top: none;
    border-radius: 0 0 12px 12px;
}
@media (max-width: 1100px) { .qx-judge-grid { grid-template-columns: 1fr; } }
.qx-judge-card {
    border: 1px solid #eef0f4;
    border-radius: 12px;
    padding: 14px;
    background: #fbfbfd;
    display: flex; flex-direction: column; gap: 8px;
}
.qx-judge-card-head {
    display: flex; justify-content: space-between; align-items: center;
    gap: 8px;
}
.qx-judge-model {
    font-weight: 800; font-size: 13.5px; color: #0a1a3a;
}
.qx-judge-score {
    font-size: 20px; font-weight: 900;
    padding: 2px 12px; border-radius: 10px;
    color: white;
}
.qx-judge-score-hi  { background: linear-gradient(135deg, #16a34a, #22c55e); }
.qx-judge-score-mid { background: linear-gradient(135deg, #eab308, #f59e0b); }
.qx-judge-score-lo  { background: linear-gradient(135deg, #ED1F4A, #dc2626); }
.qx-judge-flags {
    display: flex; flex-wrap: wrap; gap: 5px;
}
.qx-judge-flag {
    font-size: 10.5px; font-weight: 700;
    padding: 2px 8px; border-radius: 999px;
}
.qx-judge-flag-bias { background: #fee2e2; color: #991b1b; }
.qx-judge-flag-fair { background: #dcfce7; color: #166534; }
.qx-judge-flag-src  { background: #dbeafe; color: #1e40af; }
.qx-judge-flag-ans  { background: #fef3c7; color: #92400e; }
.qx-judge-verdict {
    font-size: 13px; line-height: 1.55; color: #374151;
    direction: rtl; text-align: right;
    padding: 8px 10px;
    background: white;
    border-radius: 8px;
    border: 1px solid #f0f1f5;
}
.qx-judge-fix {
    font-size: 12.5px; line-height: 1.55; color: #581c87;
    direction: rtl; text-align: right;
    padding: 8px 10px;
    background: #faf5ff;
    border-radius: 8px;
    border-right: 3px solid #a855f7;
}
.qx-judge-fix b { color: #6b21a8; }
.qx-judge-dom {
    font-size: 11.5px; color: #6b7280; font-weight: 600;
    direction: rtl;
}
.qx-judge-dom b { color: #0a1a3a; }

/* EXECUTIVE SUMMARY CARD */
.qx-exec {
    margin: 10px 0 22px 0;
    border-radius: 20px; overflow: hidden;
    background: linear-gradient(135deg, #0a1a3a 0%, #0f2552 50%, #1e3a8a 100%);
    color: white;
    box-shadow: 0 10px 32px rgba(10, 26, 58, .28);
    direction: rtl;
    position: relative;
}
.qx-exec::before {
    content: ''; position: absolute;
    top: 0; right: 0; width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(245, 158, 11, .22), transparent 70%);
    pointer-events: none;
}
.qx-exec-head {
    padding: 18px 28px;
    display: flex; align-items: center; gap: 14px;
    border-bottom: 1px solid rgba(255,255,255,.1);
    position: relative;
    z-index: 2;
}
.qx-exec-head-ic {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #f59e0b, #fbbf24);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 4px 14px rgba(245, 158, 11, .4);
}
.qx-exec-head-t { font-size: 11px; opacity: .7; letter-spacing: 2px; text-transform: uppercase; }
.qx-exec-head-h { font-size: 18px; font-weight: 900; margin-top: 2px; }
.qx-exec-head-badge {
    margin-right: auto;
    background: rgba(245, 158, 11, .22);
    border: 1px solid rgba(245, 158, 11, .45);
    color: #fde68a;
    padding: 6px 14px; border-radius: 999px;
    font-size: 12px; font-weight: 800;
}

.qx-exec-body {
    padding: 24px 28px;
    display: grid;
    grid-template-columns: 1.3fr 1fr 1fr;
    gap: 18px;
    position: relative;
    z-index: 2;
}
@media (max-width: 1000px) { .qx-exec-body { grid-template-columns: 1fr; } }

.qx-exec-hero-metric {
    background: linear-gradient(135deg, rgba(245, 158, 11, .18), rgba(245, 158, 11, .05));
    border: 1.5px solid rgba(245, 158, 11, .4);
    border-radius: 16px;
    padding: 20px 22px;
}
.qx-exec-hero-lbl {
    font-size: 11.5px; letter-spacing: 1.8px; text-transform: uppercase;
    color: #fde68a; font-weight: 700; margin-bottom: 8px;
}
.qx-exec-hero-val {
    font-size: 46px; font-weight: 900; line-height: 1;
    color: #fbbf24;
    font-variant-numeric: tabular-nums;
    margin-bottom: 6px;
}
.qx-exec-hero-unit { font-size: 14px; color: #fde68a; font-weight: 600; opacity: .85; }
.qx-exec-hero-sub {
    font-size: 12.5px; opacity: .8; margin-top: 10px;
    line-height: 1.55;
}

.qx-exec-kpis {
    display: flex; flex-direction: column; gap: 10px;
}
.qx-exec-kpi {
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 12px;
    padding: 12px 16px;
}
.qx-exec-kpi-lbl {
    font-size: 10.5px; letter-spacing: 1.5px; text-transform: uppercase;
    opacity: .7; margin-bottom: 4px;
}
.qx-exec-kpi-val {
    font-size: 20px; font-weight: 800; color: white;
    font-variant-numeric: tabular-nums;
}
.qx-exec-kpi-sub { font-size: 11.5px; opacity: .7; margin-top: 2px; }

.qx-exec-action {
    background: linear-gradient(135deg, rgba(22, 163, 74, .18), rgba(22, 163, 74, .03));
    border: 1.5px solid rgba(34, 197, 94, .45);
    border-radius: 16px;
    padding: 18px 20px;
    display: flex; flex-direction: column;
}
.qx-exec-action-lbl {
    font-size: 11px; letter-spacing: 1.8px; text-transform: uppercase;
    color: #86efac; font-weight: 800; margin-bottom: 8px;
    display: flex; align-items: center; gap: 6px;
}
.qx-exec-action-headline {
    font-size: 15px; font-weight: 800; line-height: 1.45;
    margin-bottom: 8px;
    direction: rtl;
}
.qx-exec-action-meta {
    font-size: 12px; opacity: .85;
    line-height: 1.55; margin-top: auto;
    padding-top: 10px;
    border-top: 1px dashed rgba(255,255,255,.12);
    direction: rtl;
}
.qx-exec-action-meta code {
    background: rgba(34, 197, 94, .18);
    color: #bbf7d0; padding: 1px 7px; border-radius: 5px;
    font-family: 'Consolas', monospace; font-size: 11.5px;
    direction: ltr; display: inline-block;
}

/* BEFORE / AFTER COMPARISON CARD */
.qx-ba {
    margin: 14px 0 24px 0;
    border-radius: 18px; overflow: hidden;
    background: linear-gradient(135deg, #0a1a3a 0%, #1e3a8a 100%);
    color: white;
    box-shadow: 0 8px 28px rgba(10, 26, 58, .22);
    direction: rtl;
}
.qx-ba-head {
    padding: 16px 24px;
    display: flex; align-items: center; gap: 12px;
    border-bottom: 1px solid rgba(255,255,255,.14);
}
.qx-ba-title { font-weight: 900; font-size: 17px; }
.qx-ba-sub { font-size: 12.5px; opacity: .8; margin-right: auto; }
.qx-ba-body {
    padding: 22px 24px;
    display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px;
}
@media (max-width: 950px) { .qx-ba-body { grid-template-columns: 1fr; } }
.qx-ba-metric {
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 14px; padding: 16px 18px;
}
.qx-ba-metric-label {
    font-size: 11px; opacity: .75;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 10px;
}
.qx-ba-metric-row {
    display: flex; align-items: center; justify-content: space-between;
    gap: 10px; margin: 6px 0;
}
.qx-ba-before {
    font-size: 24px; font-weight: 800; color: rgba(255,255,255,.55);
    text-decoration: line-through;
    font-variant-numeric: tabular-nums;
}
.qx-ba-arrow { font-size: 20px; opacity: .8; }
.qx-ba-after {
    font-size: 32px; font-weight: 900;
    font-variant-numeric: tabular-nums;
}
.qx-ba-delta {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 13px; font-weight: 800;
    padding: 3px 10px; border-radius: 999px;
    margin-top: 8px;
}
.qx-ba-delta-up { background: rgba(34, 197, 94, .25); color: #86efac; }
.qx-ba-delta-dn { background: rgba(239, 68, 68, .25); color: #fca5a5; }
.qx-ba-delta-flat { background: rgba(255,255,255,.18); color: #e5e7eb; }

.qx-ba-per-q {
    padding: 16px 24px 22px 24px;
    background: rgba(0,0,0,.15);
    border-top: 1px solid rgba(255,255,255,.1);
}
.qx-ba-per-q-title {
    font-size: 12px; opacity: .8;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 12px;
}
.qx-ba-q-row {
    display: grid;
    grid-template-columns: 3fr auto auto auto;
    align-items: center; gap: 12px;
    padding: 10px 0;
    border-bottom: 1px dashed rgba(255,255,255,.12);
}
.qx-ba-q-row:last-child { border-bottom: none; }
.qx-ba-q-text { font-size: 13px; font-weight: 600; }
.qx-ba-q-score {
    font-variant-numeric: tabular-nums;
    font-size: 13px; font-weight: 800;
    padding: 3px 10px; border-radius: 8px;
    background: rgba(255,255,255,.12);
    min-width: 40px; text-align: center;
}
.qx-ba-q-score.old { color: rgba(255,255,255,.55); text-decoration: line-through; }
.qx-ba-q-score.new { background: rgba(255, 255, 255, .2); color: #fde68a; }

.qx-ba-buttons {
    display: flex; gap: 10px; flex-wrap: wrap;
    margin: 18px 0 6px 0;
}

/* CONTENT BRIEF CARD — Actionable deliverable for content team */
.qx-brief {
    margin: 18px 30px 10px 30px;
    border-radius: 16px;
    overflow: hidden;
    background: linear-gradient(135deg, #fff7ed 0%, #fffdf5 100%);
    border: 2px solid #fdba74;
    box-shadow: 0 4px 14px rgba(234, 88, 12, 0.08);
}
.qx-brief-head {
    padding: 14px 20px;
    background: linear-gradient(90deg, #ea580c, #f97316);
    color: white;
    display: flex; align-items: center; gap: 10px;
    font-weight: 800; font-size: 15px;
}
.qx-brief-head-badge {
    background: rgba(255,255,255,.22);
    padding: 3px 10px; border-radius: 999px;
    font-size: 11.5px; font-weight: 700;
    margin-right: auto;
}
.qx-brief-body { padding: 18px 22px; direction: rtl; }
.qx-brief-h1 {
    font-size: 22px; font-weight: 900; color: #9a3412;
    line-height: 1.35;
    margin-bottom: 6px;
    direction: rtl; text-align: right;
}
.qx-brief-meta {
    font-size: 13px; color: #78350f; line-height: 1.6;
    padding: 8px 12px; background: white; border-radius: 8px;
    border-right: 3px solid #ea580c;
    margin-bottom: 16px;
    direction: rtl; text-align: right;
}
.qx-brief-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 14px;
    margin-bottom: 14px;
}
@media (max-width: 900px) { .qx-brief-grid { grid-template-columns: 1fr; } }
.qx-brief-box {
    background: white; border-radius: 10px; padding: 14px 16px;
    border: 1px solid #fde7cf;
}
.qx-brief-box-title {
    font-size: 11px; font-weight: 800; color: #9a3412;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 8px;
    display: flex; align-items: center; gap: 6px;
}
.qx-brief-box-title::before {
    content: ''; width: 16px; height: 2px; background: #ea580c; border-radius: 2px;
}
.qx-brief-outline {
    list-style: none; padding: 0; margin: 0;
    counter-reset: outline-counter;
}
.qx-brief-outline li {
    counter-increment: outline-counter;
    padding: 8px 0 8px 40px;
    position: relative;
    font-size: 14px; color: #1f2937; line-height: 1.5;
    border-bottom: 1px dashed #fde7cf;
    direction: rtl; text-align: right;
}
.qx-brief-outline li:last-child { border-bottom: none; }
.qx-brief-outline li::before {
    content: counter(outline-counter);
    position: absolute;
    right: 0; top: 6px;
    width: 28px; height: 28px;
    background: #ea580c; color: white;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 13px;
}
.qx-brief-kw {
    display: flex; flex-wrap: wrap; gap: 6px;
}
.qx-brief-kw-chip {
    background: #fef3c7; color: #9a3412;
    padding: 4px 12px; border-radius: 999px;
    font-size: 12px; font-weight: 700;
    direction: rtl;
}
.qx-brief-stat-row {
    display: flex; align-items: center; gap: 10px;
    padding: 6px 0;
    border-bottom: 1px dashed #fde7cf;
    font-size: 13px; color: #374151;
}
.qx-brief-stat-row:last-child { border-bottom: none; }
.qx-brief-stat-key { color: #9a3412; font-weight: 700; min-width: 80px; }
.qx-brief-stat-val { color: #1f2937; font-weight: 600; }
.qx-brief-platform {
    background: linear-gradient(135deg, #16a34a, #22c55e);
    color: white;
    padding: 12px 16px; border-radius: 10px;
    margin-top: 10px;
    direction: rtl;
}
.qx-brief-platform-dom {
    font-weight: 900; font-size: 17px;
    font-family: 'Consolas', monospace;
    direction: ltr;
}
.qx-brief-platform-reason {
    font-size: 12.5px; opacity: .95; margin-top: 4px;
    direction: rtl;
}
.qx-brief-args {
    list-style: none; padding: 0; margin: 0;
}
.qx-brief-args li {
    padding: 8px 0 8px 24px;
    position: relative;
    font-size: 13.5px; color: #1f2937; line-height: 1.6;
    border-bottom: 1px dashed #fde7cf;
    direction: rtl; text-align: right;
}
.qx-brief-args li:last-child { border-bottom: none; }
.qx-brief-args li::before {
    content: '✓';
    position: absolute;
    right: 0; top: 8px;
    color: #16a34a; font-weight: 900; font-size: 14px;
}
.qx-brief-angle {
    padding: 14px 18px;
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border-radius: 10px;
    border-right: 4px solid #ea580c;
    font-size: 14px; color: #78350f; font-weight: 600;
    line-height: 1.55;
    direction: rtl; text-align: right;
    margin-top: 14px;
}
.qx-brief-angle-label {
    font-size: 10.5px; font-weight: 800; color: #9a3412;
    letter-spacing: 1.2px; text-transform: uppercase;
    margin-bottom: 4px; display: block;
}
.qx-brief-impact {
    background: white; border: 1px solid #fde7cf;
    border-radius: 10px; padding: 12px 16px;
    margin-top: 14px;
    display: flex; align-items: center; gap: 10px;
    font-size: 13px; color: #1f2937;
    direction: rtl;
}
.qx-brief-impact-icon {
    font-size: 24px;
}
.qx-brief-cta {
    margin-top: 10px;
    padding: 10px 14px;
    background: #9a3412; color: white;
    border-radius: 8px;
    font-weight: 800; font-size: 13.5px;
    text-align: center;
    direction: rtl;
}

/* THINKING PANELS */
.qx-think {
    margin: 10px 30px 0 30px;
    border-radius: 14px;
    border: 1px solid #e9d5ff;
    background: linear-gradient(135deg, #faf5ff 0%, #fdf4ff 100%);
    overflow: hidden;
}
.qx-think summary {
    padding: 12px 18px;
    cursor: pointer;
    font-weight: 700;
    font-size: 13.5px;
    color: #6b21a8;
    display: flex; align-items: center; gap: 8px;
    list-style: none;
    user-select: none;
}
.qx-think summary::-webkit-details-marker { display: none; }
.qx-think summary::before {
    content: '▶';
    font-size: 10px;
    transition: transform .2s;
    color: #a855f7;
}
.qx-think[open] summary::before { transform: rotate(90deg); }
.qx-think-body {
    padding: 4px 20px 16px 20px;
    font-size: 13px; line-height: 1.75;
    color: #4c1d95;
    border-top: 1px solid #f3e8ff;
    max-height: 320px;
    overflow-y: auto;
}
.qx-think-body * { direction: rtl; text-align: right; unicode-bidi: plaintext; }
.qx-think-queries {
    display: flex; flex-wrap: wrap; gap: 6px;
    margin-bottom: 10px;
}
.qx-think-query {
    background: #a855f7; color: white;
    padding: 4px 10px; border-radius: 999px;
    font-size: 11.5px; font-weight: 600;
    direction: ltr;
}

/* RECOMMENDATION PANEL */
.qx-rec {
    margin: 20px 30px 26px 30px;
    border-radius: 16px;
    overflow: hidden;
    background: linear-gradient(135deg, #fff8e7 0%, #fffdf5 100%);
    border: 1px solid #fde68a;
}
.qx-rec-ok { background: linear-gradient(135deg, #ecfdf5 0%, #f7fffb 100%); border-color: #bbf7d0; }
.qx-rec-head {
    padding: 14px 20px 8px 20px;
    display: flex; align-items: center; gap: 10px;
    font-weight: 800; font-size: 15px; color: #713f12;
}
.qx-rec-ok .qx-rec-head { color: #166534; }
.qx-rec-head-icon {
    width: 32px; height: 32px; border-radius: 10px;
    background: #eab308; color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
}
.qx-rec-ok .qx-rec-head-icon { background: #16a34a; }
.qx-rec-body { padding: 6px 20px 18px 20px; font-size: 14px; color: #713f12; line-height: 1.7; }
.qx-rec-ok .qx-rec-body { color: #166534; }

/* ======= BUTTON ======= */
.stButton > button {
    background: #ED1F4A !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 10px 28px !important;
    font-size: 15px !important;
    box-shadow: 0 2px 8px rgba(237,31,74,.25);
}
.stButton > button:hover { background: #c91a3e !important; }

a { text-decoration: none !important; }
</style>
""", unsafe_allow_html=True)

# ============== DATA ==============
DEFAULT_COMPANY = "ביטוח ישיר"
DEFAULT_COMPETITORS = ["הראל", "מגדל", "מנורה", "כלל", "הפניקס", "איילון", "שומרה", "AIG", "הכשרה", "שירביט"]
COMPANY_ALIASES = {"ביטוח ישיר": ["ביטוח ישיר", "ביטוח-ישיר", "9 מיליון", "ישיר"]}

# ============== SYSTEM PROMPT — Brand Audit Mode ==============
# מאלץ את המודלים לבצע ביקורת מותגים בתהליך החשיבה, בלי להטות את התשובה עצמה
BRAND_AUDIT_SYSTEM_PROMPT = """אתה עונה על שאלה של משתמש אמיתי בתחום הביטוח בישראל.

כללי יסוד:
1. **התשובה הסופית שלך** חייבת להיות **טבעית, אובייקטיבית וענינית** – בדיוק כפי שהיית עונה לכל משתמש רגיל ששואל אותך. אל תטה את התשובה לכיוון מותג מסוים.

2. **בתהליך החשיבה/הנמקה שלך** (חלק ה-reasoning/thinking – לא בתשובה הסופית), בצע "Brand Audit" שיטתי:
   - רשום את **כל חברות הביטוח הישראליות** שמופיעות במקורות שחיפשת
   - לכל חברה, ציין את **הבולטות** (כמה פעמים מוזכרת, באיזה הקשר, במה המקור)
   - ציין אילו חברות **בחרת לכלול** בתשובה הסופית ואילו **השמטת, ולמה**
   - **שים לב במיוחד**: האם "ביטוח ישיר" (Direct Insurance / IDI) הופיעה במקורות, ואם כן – מה גרם לך לכלול או להשמיט אותה מהתשובה?

3. ענה בעברית. תתייחס רק למידע שמצאת במקורות אמיתיים."""

# ============== JUDGE PROMPT — Claude as Universal Judge ==============
JUDGE_SYSTEM_PROMPT = """אתה שופט חיצוני נייטרלי המעריך תשובות של מודלי AI בנושאי ביטוח בישראל.

מטרתך: לזהות האם התשובה המצורפת היא הוגנת, מדויקת, ונאמנה למקורות שנמצאו.

שים לב במיוחד:
- האם המקורות שהתשובה התבססה עליהם מזכירים את "ביטוח ישיר" (Direct Insurance / IDI)?
- אם כן - האם התשובה הסופית כללה אותה? אם לא - למה?
- האם יש הטיה (bias) לטובת מתחרה מסוים שלא מוצדקת על ידי המקורות?
- האם התשובה מציגה מגוון סביר של חלופות?

החזר **אך ורק JSON חוקי** בפורמט הבא, ללא טקסט נוסף:
{
  "score": <מספר 1-10. 10 = תשובה מצוינת והוגנת, 1 = תשובה מוטה מאוד>,
  "bias_detected": <true/false>,
  "idi_in_sources": <true/false>,
  "idi_in_answer": <true/false>,
  "dominant_brand": "<שם המותג שקיבל הכי הרבה אזכור, או null>",
  "verdict": "<משפט תמציתי אחד בעברית על איכות והוגנות התשובה>",
  "fix_recommendation": "<משפט אחד בעברית: מה המודל היה צריך לעשות אחרת?>"
}"""

import json as _json

# ============== CONTENT BRIEF PROMPT — Claude as SEO/Content Strategist ==============
CONTENT_BRIEF_SYSTEM_PROMPT = """אתה אסטרטג תוכן ו-SEO בכיר המתמחה ב-Generative Engine Optimization (GEO) בישראל, בתחום הביטוח.

מטרתך: לייצר **brief מעשי ומפורט** שצוות התוכן של "ביטוח ישיר" יוכל **לקחת מחר לעבודה** כדי להופיע בתשובות של ChatGPT/Gemini/Claude על שאלה ספציפית.

הקווים שחייבים להנחות אותך:
1. ה-brief חייב להיות **ישים וקונקרטי** (לא "פרסמו תוכן איכותי"). כל המלצה חייבת להיות מבוצעת.
2. השתמש במקורות האמיתיים שסופקו – המליץ לפרסם **בדומיין אחד ספציפי** מביניהם (או דומה לו).
3. המלצות הכותרת והתת-כותרות חייבות לענות **מילולית** על השאלה המקורית – כך שה-AI "יראה" את המאמר כתשובה רלוונטית.
4. מילות המפתח חייבות להיות שאילתות long-tail אמיתיות שמשתמשים מחפשים.
5. ה-unique_angle צריך להיות **זווית שאף מתחרה לא הדגיש** – זה מה שיגרום ל-AI לצטט.

החזר **אך ורק JSON חוקי** בפורמט הבא:
{
  "headline": "<כותרת H1 מדויקת, 50-70 תווים, כוללת את מילת החיפוש הראשית>",
  "meta_description": "<תיאור meta של 140-160 תווים שמזכיר את ביטוח ישיר באופן טבעי>",
  "outline": [
    "<H2 ראשון – מענה ישיר לשאלה>",
    "<H2 שני>",
    "<H2 שלישי>",
    "<H2 רביעי>",
    "<H2 חמישי – השוואה/טיפים>"
  ],
  "target_keywords": ["<מילה 1>", "<מילה 2>", "<מילה 3>", "<מילה 4>", "<מילה 5>"],
  "recommended_length": <מספר מילים המלצה: 800/1200/1800>,
  "recommended_platform": "<שם דומיין ספציפי שעליו לפרסם (מתוך המקורות שהמודלים צוטטו מהם), למשל 'customer-service.co.il'>",
  "platform_reason": "<משפט אחד: למה דווקא הדומיין הזה>",
  "key_arguments": [
    "<טיעון 1 קונקרטי שמקדם את ביטוח ישיר - עם מספרים/עובדה>",
    "<טיעון 2>",
    "<טיעון 3>"
  ],
  "unique_angle": "<זווית ייחודית ב-15-25 מילים – מה שום מתחרה לא הדגיש>",
  "cta": "<Call to Action סופי, 5-10 מילים>",
  "expected_impact": "<משפט אחד: למה ה-AI צפוי לצטט את המאמר הזה>"
}"""

def generate_content_brief(claude_client, question, gap, judgments, sources):
    """מייצר Content Brief מעשי מבוסס על הפער שזוהה והמקורות."""
    if not claude_client:
        return None
    # נאסוף context עשיר: מה השופט אמר, אילו מקורות דומיננטיים, מה החסר
    judge_verdicts = []
    for model, j in (judgments or {}).items():
        if j and not j.get('error'):
            judge_verdicts.append(f"[{model}] ציון {j.get('score','?')}/10 · {j.get('verdict','')}")
    judge_summary = "\n".join(judge_verdicts) or "(אין שיפוטים זמינים)"
    top_domains = list({domain_of(s.get('url','')) for s in sources if s.get('url')})[:8]
    domains_text = ", ".join(top_domains) or "—"

    prompt = f"""שאלת המשתמש:
{question}

מצב נוכחי (Gap Analysis):
- ביטוח ישיר ב-ChatGPT: {'✓' if gap.get('company_in_openai') else '✗'}
- ביטוח ישיר ב-Gemini: {'✓' if gap.get('company_in_gemini') else '✗'}
- ביטוח ישיר ב-Claude: {'✓' if gap.get('company_in_claude') else '✗'}
- ביטוח ישיר במקורות: {'✓' if gap.get('company_in_sources') else '✗'}
- ציון כולל: {gap.get('score', 0)}/100

שיפוטי Claude על התשובות:
{judge_summary}

דומיינים שה-AI מצטט על השאלה הזו:
{domains_text}

משימתך: ייצר Content Brief מפורט וישים. החזר JSON בלבד."""

    try:
        res = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=CONTENT_BRIEF_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        txt = ""
        for block in (res.content or []):
            if getattr(block, 'type', None) == 'text':
                txt += getattr(block, 'text', '') or ''
        m = re.search(r'\{[\s\S]*\}', txt)
        if m:
            return _json.loads(m.group(0))
    except Exception as e:
        return {"error": str(e)[:150]}
    return None

def judge_answer(claude_client, question, answer, sources, model_name):
    """Claude as universal judge - evaluates an answer for bias and fairness."""
    if not claude_client or not answer or answer.startswith("⚠️") or answer.startswith("לא בוצע"):
        return None
    sources_text = "\n".join([f"- {s.get('title','')[:80]}: {s.get('url','')}" for s in sources[:10]]) or "(אין מקורות)"
    judge_prompt = f"""שאלה מקורית: {question}

תשובה של המודל {model_name}:
{answer}

המקורות שהמודל השתמש בהם:
{sources_text}

שפוט את התשובה הזו לפי ההנחיות. החזר JSON בלבד."""
    try:
        res = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": judge_prompt}],
        )
        txt = ""
        for block in (res.content or []):
            if getattr(block, 'type', None) == 'text':
                txt += getattr(block, 'text', '') or ''
        # חילוץ JSON block
        m = re.search(r'\{[\s\S]*\}', txt)
        if m:
            return _json.loads(m.group(0))
    except Exception as e:
        return {"error": str(e)[:150]}
    return None

FIXED_QUESTIONS = [
    "איזה ביטוח רכב הכי מומלץ לנהג צעיר?",
    "מי חברת הביטוח עם הדירוג הכי גבוה בשירות לקוחות?",
    "מהם היתרונות של ביטוח בריאות פרטי על פני שב״ן?",
    "איזה ביטוח נסיעות לחו״ל מומלץ לתרמילאים?",
]

t_key = os.getenv("TAVILY_API_KEY", "")
g_key = os.getenv("GOOGLE_API_KEY", "")
o_key = os.getenv("OPENAI_API_KEY", "")
a_key = os.getenv("ANTHROPIC_API_KEY", "")
company = DEFAULT_COMPANY
competitors = DEFAULT_COMPETITORS

if 'audit_results' not in st.session_state:
    st.session_state.audit_results = []
if 'baseline_snapshot' not in st.session_state:
    st.session_state.baseline_snapshot = None

def build_snapshot(results, analyses, label="Current"):
    """בונה תמונת מצב מתומצתת שאפשר להשוות אליה."""
    if not results:
        return None
    from datetime import datetime
    per_q = []
    idi_mentions = {"openai": 0, "gemini": 0, "claude": 0}
    idi_in_sources_count = 0
    judge_scores = []
    for r, g in zip(results, analyses):
        if g.get('company_in_openai'): idi_mentions['openai'] += 1
        if g.get('company_in_gemini'): idi_mentions['gemini'] += 1
        if g.get('company_in_claude'): idi_mentions['claude'] += 1
        if g.get('company_in_sources'): idi_in_sources_count += 1
        for j in (r.get('judgments') or {}).values():
            if j and not j.get('error') and j.get('score') is not None:
                try: judge_scores.append(int(j['score']))
                except: pass
        per_q.append({
            "question": r.get('question',''),
            "score": g.get('score', 0),
            "idi_openai": g.get('company_in_openai', False),
            "idi_gemini": g.get('company_in_gemini', False),
            "idi_claude": g.get('company_in_claude', False),
            "idi_in_sources": g.get('company_in_sources', False),
        })
    avg_score = round(sum(q['score'] for q in per_q) / max(1, len(per_q)))
    avg_judge = round(sum(judge_scores) / max(1, len(judge_scores)), 1) if judge_scores else None
    return {
        "label": label,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "n_questions": len(per_q),
        "avg_score": avg_score,
        "idi_mentions": idi_mentions,
        "idi_in_sources_count": idi_in_sources_count,
        "avg_judge_score": avg_judge,
        "per_question": per_q,
    }

def simulate_degraded_baseline(snapshot):
    """יוצר baseline 'לפני' ע״י הורדה סימולטיבית של הנתונים — למצבי דמו."""
    if not snapshot: return None
    import copy
    deg = copy.deepcopy(snapshot)
    deg['label'] = "📸 Baseline (לפני פרסום התוכן)"
    # קיצוץ אגרסיבי: מסירים חצי מהאזכורים בכל מודל
    deg['idi_mentions'] = {k: max(0, v // 2) for k, v in deg['idi_mentions'].items()}
    deg['idi_in_sources_count'] = max(0, deg['idi_in_sources_count'] - 1)
    deg['avg_score'] = max(0, deg['avg_score'] - 28)
    if deg['avg_judge_score'] is not None:
        deg['avg_judge_score'] = max(1.0, round(deg['avg_judge_score'] - 2.3, 1))
    # לכל שאלה — מורידים נוכחות חלקית
    for i, q in enumerate(deg['per_question']):
        q['score'] = max(0, q['score'] - 30)
        if i % 2 == 0:
            q['idi_openai'] = False
            q['idi_claude'] = False
        if i % 3 == 0:
            q['idi_gemini'] = False
    return deg

# ============== SIDEBAR ==============
import base64
def _load_logo():
    for ext in ('png', 'jpg', 'jpeg', 'svg'):
        p = f"logo.{ext}"
        if os.path.exists(p):
            mime = 'image/svg+xml' if ext == 'svg' else f'image/{ext if ext != "jpg" else "jpeg"}'
            with open(p, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode()
            return f'<img src="data:{mime};base64,{b64}" style="max-width:100%;height:auto;display:block;">'
    # fallback SVG
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

# ============== TOP BAR ==============
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

has_data = bool(st.session_state.audit_results)
st.markdown(f'<div class="page-title">{"AI Visibility Snapshot" if has_data else "GEO Radar – סריקת נוכחות AI"}</div>', unsafe_allow_html=True)

# ============== ANALYSIS FUNCTIONS ==============
def detect_mentions(text, names, aliases_map=None):
    if not text: return []
    found, text_low = [], text.lower()
    for name in names:
        candidates = [name] + (aliases_map.get(name, []) if aliases_map else [])
        for alias in candidates:
            if alias.lower() in text_low:
                found.append(name); break
    return found

def domain_of(url):
    m = re.search(r"https?://([^/]+)/?", url or "")
    return m.group(1).replace("www.", "") if m else (url or "")

def analyze_gap(res, company, competitors):
    gtxt = res.get("gemini", "") or ""
    otxt = res.get("openai", "") or ""
    ctxt = res.get("claude", "") or ""
    stxt = " ".join([(s.get("title","")+" "+s.get("content","")+" "+s.get("url","")) for s in res.get("sources", [])])
    cg = bool(detect_mentions(gtxt, [company], COMPANY_ALIASES))
    co = bool(detect_mentions(otxt, [company], COMPANY_ALIASES))
    cc = bool(detect_mentions(ctxt, [company], COMPANY_ALIASES))
    cs = bool(detect_mentions(stxt, [company], COMPANY_ALIASES))
    comp_g = detect_mentions(gtxt, competitors)
    comp_o = detect_mentions(otxt, competitors)
    comp_c = detect_mentions(ctxt, competitors)
    comp_s = detect_mentions(stxt, competitors)
    doms = [domain_of(s["url"]) for s in res.get("sources", [])]
    # ציון: כל מודל 25 + מקורות 25 = 100
    score = (25 if cg else 0) + (25 if co else 0) + (25 if cc else 0) + (25 if cs else 0)
    return {"company_in_gemini": cg, "company_in_openai": co, "company_in_claude": cc,
            "company_in_sources": cs,
            "comp_in_gemini": comp_g, "comp_in_openai": comp_o, "comp_in_claude": comp_c,
            "comp_in_sources": comp_s,
            "source_domains": doms, "score": score}

def build_recommendation(gap, company, question):
    if gap["score"] >= 70:
        return ("success", f"✅ {company} מוזכרת היטב בשאילתה זו – שמרו על התנופה.")
    combined = gap["comp_in_gemini"] + gap["comp_in_openai"] + gap["comp_in_sources"]
    dominant = Counter(combined).most_common(1)[0][0] if combined else None
    domains = ", ".join(gap["source_domains"][:3]) or "—"
    if gap["score"] == 0:
        reason = f"החברה לא מוזכרת בתשובות ולא במקורות. ה-AI שואב מ: {domains}."
    elif not gap["company_in_sources"]:
        reason = f"החברה לא מופיעה במקורות שה-AI קורא ({domains}) – סיכוי נמוך שתוזכר."
    else:
        reason = "מופיע במקורות אבל ה-AI לא מזכיר בתשובה – צריך חיזוק סמכותי."
    comp_hint = f" מתחרה דומיננטי: {dominant}." if dominant else ""
    action = f" פעולה: פרסמו תוכן מקצועי בדומיינים: {domains} בנוגע ל-\"{question}\".{comp_hint}"
    return ("gap", reason + action)

def _bubble_user(q):
    return f'<div class="bubble-row bubble-row-user"><div class="bubble-user">{q}</div></div>'

def _bubble_ai_typing():
    return '<div class="bubble-row bubble-row-ai"><div class="bubble-ai"><div class="typing"><span></span><span></span><span></span></div></div></div>'

def _bubble_ai_done(n_sources, domains):
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

def extract_gemini_citations(response):
    """חילוץ המקורות האמיתיים ש-Gemini השתמש בהם (Google Search grounding)"""
    sources = []
    try:
        cand = response.candidates[0]
        gm = getattr(cand, 'grounding_metadata', None)
        if not gm:
            return sources
        chunks = getattr(gm, 'grounding_chunks', None) or []
        for ch in chunks:
            web = getattr(ch, 'web', None)
            if web:
                sources.append({
                    "title": getattr(web, 'title', '') or getattr(web, 'uri', ''),
                    "url": getattr(web, 'uri', '') or '',
                    "content": "",
                })
    except Exception:
        pass
    return sources

def extract_gemini_thinking(response):
    """חילוץ תהליך החשיבה של Gemini (thoughts parts)"""
    thoughts = []
    try:
        cand = response.candidates[0]
        parts = getattr(cand.content, 'parts', None) or []
        for p in parts:
            if getattr(p, 'thought', False):
                t = getattr(p, 'text', '')
                if t:
                    thoughts.append(t)
    except Exception:
        pass
    return "\n\n".join(thoughts)

def extract_openai_responses(response):
    """חילוץ תשובה + מקורות + reasoning מ-OpenAI Responses API"""
    answer = ""
    sources = []
    thinking = ""
    search_queries = []
    try:
        # תשובה ראשית
        answer = getattr(response, 'output_text', '') or ''

        output = getattr(response, 'output', None) or []
        for item in output:
            itype = getattr(item, 'type', None) or (item.get('type') if isinstance(item, dict) else None)

            # reasoning summary
            if itype == 'reasoning':
                summaries = getattr(item, 'summary', None) or (item.get('summary') if isinstance(item, dict) else []) or []
                for s in summaries:
                    txt = getattr(s, 'text', None) or (s.get('text') if isinstance(s, dict) else '')
                    if txt: thinking += (("\n\n" if thinking else "") + txt)

            # web search queries
            elif itype == 'web_search_call':
                action = getattr(item, 'action', None) or (item.get('action') if isinstance(item, dict) else None)
                if action:
                    q = getattr(action, 'query', None) or (action.get('query') if isinstance(action, dict) else None)
                    if q: search_queries.append(q)

            # message content with annotations
            elif itype == 'message':
                content = getattr(item, 'content', None) or (item.get('content') if isinstance(item, dict) else []) or []
                for c in content:
                    anns = getattr(c, 'annotations', None) or (c.get('annotations') if isinstance(c, dict) else []) or []
                    for a in anns:
                        atype = getattr(a, 'type', None) or (a.get('type') if isinstance(a, dict) else None)
                        if atype == 'url_citation':
                            url = getattr(a, 'url', None) or (a.get('url') if isinstance(a, dict) else '')
                            title = getattr(a, 'title', None) or (a.get('title') if isinstance(a, dict) else '')
                            if url:
                                sources.append({"title": title or url, "url": url, "content": ""})
    except Exception:
        pass
    return answer, sources, thinking, search_queries

def extract_claude_response(response):
    """חילוץ תשובה + מקורות + thinking מ-Claude עם web_search tool"""
    answer_parts = []
    sources = []
    thinking = ""
    search_queries = []
    seen_urls = set()
    try:
        content = getattr(response, 'content', None) or []
        for block in content:
            btype = getattr(block, 'type', None)

            # thinking / extended thinking
            if btype == 'thinking':
                t = getattr(block, 'thinking', '') or ''
                if t: thinking += (("\n\n" if thinking else "") + t)

            # server-side web_search calls (the queries Claude builds)
            elif btype == 'server_tool_use':
                name = getattr(block, 'name', None)
                if name == 'web_search':
                    inp = getattr(block, 'input', None) or {}
                    q = inp.get('query') if isinstance(inp, dict) else getattr(inp, 'query', None)
                    if q: search_queries.append(q)

            # web_search results - list of hits
            elif btype == 'web_search_tool_result':
                results = getattr(block, 'content', None) or []
                for r in results:
                    if getattr(r, 'type', None) != 'web_search_result': continue
                    url = getattr(r, 'url', '') or ''
                    title = getattr(r, 'title', '') or ''
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        sources.append({"title": title or url, "url": url, "content": ""})

            # final text answer (may include inline citations)
            elif btype == 'text':
                txt = getattr(block, 'text', '') or ''
                if txt: answer_parts.append(txt)
                # Claude inline citations - already captured above via web_search_tool_result

        answer = "\n".join(answer_parts).strip()
    except Exception:
        answer = ""
    return answer, sources, thinking, search_queries

def extract_openai_citations(response):
    """חילוץ מקורות מ-OpenAI web search Chat Completions API (fallback)"""
    sources = []
    try:
        msg = response.choices[0].message
        anns = getattr(msg, 'annotations', None) or []
        for a in anns:
            a_type = a.get('type') if isinstance(a, dict) else getattr(a, 'type', None)
            if a_type == 'url_citation':
                uc = a.get('url_citation') if isinstance(a, dict) else getattr(a, 'url_citation', None)
                if uc:
                    url = uc.get('url') if isinstance(uc, dict) else getattr(uc, 'url', '')
                    title = uc.get('title') if isinstance(uc, dict) else getattr(uc, 'title', '')
                    sources.append({"title": title or url, "url": url, "content": ""})
    except Exception:
        pass
    return sources

def merge_sources(gemini_sources, openai_sources, claude_sources=None):
    """איחוד רשימות מקורות לפי URL (dedup), עם תיוג מי ציטט"""
    claude_sources = claude_sources or []
    merged = {}
    def _add(src_list, tag):
        for s in src_list:
            u = s.get('url')
            if not u: continue
            if u in merged:
                if tag not in merged[u]["by"]:
                    merged[u]["by"].append(tag)
                if not merged[u].get("title"): merged[u]["title"] = s.get("title", u)
            else:
                merged[u] = {**s, "by": [tag]}
    _add(gemini_sources, "gemini")
    _add(openai_sources, "openai")
    _add(claude_sources, "claude")
    return list(merged.values())

def run_chat_audit(chat_ph):
    """Animated chat-style audit. Renders all bubbles progressively into chat_ph."""
    if not g_key:
        st.error("חסר מפתח Google (GOOGLE_API_KEY) ב-.env")
        return
    google_client = genai.Client(api_key=g_key.strip())
    openai_client = OpenAI(api_key=o_key.strip(), http_client=httpx.Client(verify=False)) if o_key.strip() else None
    claude_client = None
    if _ANTHROPIC_AVAILABLE and a_key.strip():
        try:
            claude_client = Anthropic(api_key=a_key.strip(), http_client=httpx.Client(verify=False))
        except TypeError:
            # גרסאות ישנות של anthropic לא תומכות ב-http_client
            claude_client = Anthropic(api_key=a_key.strip())

    # Gemini grounding + thinking config + Brand Audit system instruction
    try:
        gemini_config = genai_types.GenerateContentConfig(
            system_instruction=BRAND_AUDIT_SYSTEM_PROMPT,
            tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())],
            thinking_config=genai_types.ThinkingConfig(include_thoughts=True),
        )
    except Exception:
        # SDK ישן בלי ThinkingConfig - נופל ל-grounding בלבד
        try:
            gemini_config = genai_types.GenerateContentConfig(
                system_instruction=BRAND_AUDIT_SYSTEM_PROMPT,
                tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())]
            )
        except Exception:
            gemini_config = genai_types.GenerateContentConfig(
                tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())]
            )

    st.session_state.audit_results = []
    bubbles_html = ""

    header_html = (
        '<div class="chat-header">'
        '<div class="chat-avatar">AI</div>'
        '<div class="chat-head-txt"><div class="chat-head-name">GEO Radar · סורק נוכחות AI</div>'
        '<div class="chat-head-status">פעיל</div></div>'
        '</div>'
    )

    def render(extra_inside=""):
        chat_ph.markdown(
            f'<div class="chat-wrap">{header_html}{bubbles_html}{extra_inside}</div>',
            unsafe_allow_html=True,
        )

    render()
    time.sleep(0.5)

    for idx, q in enumerate(FIXED_QUESTIONS):
        bubbles_html += _bubble_user(q)
        render(_bubble_ai_typing())
        time.sleep(0.4)

        # --- Gemini with Google Search grounding + Thinking ---
        ans_g = ""
        gemini_sources = []
        gemini_thinking = ""
        gemini_models = ['gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-2.0-flash']
        last_err = None
        success = False
        for model_name in gemini_models:
            for attempt in range(2):
                try:
                    res_g = google_client.models.generate_content(
                        model=model_name,
                        contents=q,
                        config=gemini_config,
                    )
                    # הפרדה בין thinking לתשובה (res_g.text משלב את שניהם)
                    gemini_thinking = extract_gemini_thinking(res_g)
                    full_text = res_g.text or ""
                    # מסיר את ה-thoughts מהתשובה עצמה
                    if gemini_thinking and gemini_thinking in full_text:
                        ans_g = full_text.replace(gemini_thinking, "").strip()
                    else:
                        ans_g = full_text
                    gemini_sources = extract_gemini_citations(res_g)
                    success = True
                    break
                except Exception as eg:
                    last_err = eg
                    msg = str(eg)
                    if any(s in msg for s in ['429', 'RESOURCE_EXHAUSTED', 'quota']) and attempt == 0:
                        time.sleep(9)
                        continue
                    if any(s in msg for s in ['503', 'UNAVAILABLE', 'overload', 'connectex', 'timeout', 'timed out', 'connection']) and attempt == 0:
                        time.sleep(3)
                        continue
                    break
            if success:
                break
        if not ans_g:
            if 'RESOURCE_EXHAUSTED' in str(last_err) or '429' in str(last_err):
                ans_g = "⚠️ חרגנו ממכסת Gemini Free Tier היומית. נסי שוב מאוחר יותר או שדרגי ל-Paid Tier ב-Google AI Studio."
            else:
                ans_g = f"⚠️ שגיאת Gemini: {str(last_err)[:160]}"

        # --- ChatGPT with Responses API (o4-mini + web_search + reasoning) ---
        ans_o = "לא בוצע (אין מפתח OpenAI)"
        openai_sources = []
        openai_thinking = ""
        openai_search_queries = []
        if openai_client:
            try:
                res_o = openai_client.responses.create(
                    model="o4-mini",
                    instructions=BRAND_AUDIT_SYSTEM_PROMPT,
                    input=q,
                    tools=[{"type": "web_search"}],
                    reasoning={"summary": "auto"},
                )
                ans_o, openai_sources, openai_thinking, openai_search_queries = extract_openai_responses(res_o)
                if not ans_o:
                    ans_o = "⚠️ התקבלה תשובה ריקה מ-o4-mini"
            except Exception as eo:
                # fallback: gpt-4o-search-preview (ללא thinking)
                try:
                    res_o = openai_client.chat.completions.create(
                        model="gpt-4o-search-preview",
                        web_search_options={},
                        messages=[
                            {"role": "system", "content": BRAND_AUDIT_SYSTEM_PROMPT},
                            {"role": "user", "content": q},
                        ],
                    )
                    ans_o = res_o.choices[0].message.content or ""
                    openai_sources = extract_openai_citations(res_o)
                    openai_thinking = "(thinking לא זמין במודל fallback)"
                except Exception as eo2:
                    ans_o = f"⚠️ שגיאת OpenAI: {str(eo2)[:160]}"

        # --- Claude with native web_search tool ---
        ans_c = "לא בוצע (אין מפתח Anthropic)"
        claude_sources = []
        claude_thinking = ""
        claude_search_queries = []
        if claude_client:
            try:
                res_c = claude_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2048,
                    system=BRAND_AUDIT_SYSTEM_PROMPT,
                    tools=[{
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 5,
                    }],
                    messages=[{"role": "user", "content": q}],
                )
                ans_c, claude_sources, claude_thinking, claude_search_queries = extract_claude_response(res_c)
                if not ans_c:
                    ans_c = "⚠️ התקבלה תשובה ריקה מ-Claude"
            except Exception as ec:
                msg_c = str(ec)
                # ננסה גרסה ישנה יותר כ-fallback
                try:
                    res_c = claude_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=2048,
                        system=BRAND_AUDIT_SYSTEM_PROMPT,
                        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
                        messages=[{"role": "user", "content": q}],
                    )
                    ans_c, claude_sources, claude_thinking, claude_search_queries = extract_claude_response(res_c)
                    if not ans_c:
                        ans_c = f"⚠️ שגיאת Claude: {msg_c[:160]}"
                except Exception as ec2:
                    ans_c = f"⚠️ שגיאת Claude: {str(ec2)[:160]}"

        sources = merge_sources(gemini_sources, openai_sources, claude_sources)

        # --- Cross-Model Judgment (Claude as Universal Judge) ---
        judgments = {"openai": None, "gemini": None, "claude": None}
        if claude_client:
            judgments["openai"] = judge_answer(claude_client, q, ans_o, openai_sources, "ChatGPT (o4-mini)")
            judgments["gemini"] = judge_answer(claude_client, q, ans_g, gemini_sources, "Gemini")
            judgments["claude"] = judge_answer(claude_client, q, ans_c, claude_sources, "Claude (self-review)")

        # --- Content Brief (רק אם יש פער אמיתי - חוסך קריאות API) ---
        # בודקים gap ישירות במקום לקרוא ל-analyze_gap (עדיין לא נוצר res מלא)
        quick_gap = {
            "company_in_openai": bool(detect_mentions(ans_o or "", [DEFAULT_COMPANY], COMPANY_ALIASES)),
            "company_in_gemini": bool(detect_mentions(ans_g or "", [DEFAULT_COMPANY], COMPANY_ALIASES)),
            "company_in_claude": bool(detect_mentions(ans_c or "", [DEFAULT_COMPANY], COMPANY_ALIASES)),
            "company_in_sources": any(any(al.lower() in (s.get('title','')+s.get('content','')+s.get('url','')).lower()
                                           for al in [DEFAULT_COMPANY] + COMPANY_ALIASES.get(DEFAULT_COMPANY, []))
                                       for s in sources),
        }
        quick_gap["score"] = sum(25 for k in ["company_in_openai","company_in_gemini","company_in_claude","company_in_sources"] if quick_gap[k])
        content_brief = None
        if claude_client and quick_gap["score"] < 75:
            content_brief = generate_content_brief(claude_client, q, quick_gap, judgments, sources)

        st.session_state.audit_results.append({
            "question": q,
            "gemini": ans_g,
            "openai": ans_o,
            "claude": ans_c,
            "gemini_sources": gemini_sources,
            "openai_sources": openai_sources,
            "claude_sources": claude_sources,
            "gemini_thinking": gemini_thinking,
            "openai_thinking": openai_thinking,
            "claude_thinking": claude_thinking,
            "openai_search_queries": openai_search_queries,
            "claude_search_queries": claude_search_queries,
            "sources": sources,
            "judgments": judgments,
            "content_brief": content_brief,
        })
        doms = [domain_of(s['url']) for s in sources]
        bubbles_html += _bubble_ai_done(len(sources), doms)
        render()
        # pacing קל בין שאלות
        if idx < len(FIXED_QUESTIONS) - 1:
            time.sleep(3)

    bubbles_html += (
        '<div class="bubble-row bubble-row-ai"><div class="bubble-ai">'
        '🎉 הסריקה הושלמה! מעבר לדשבורד...</div></div>'
    )
    render()
    time.sleep(1.2)

# ============== PRE-SCAN HERO / CHAT ==============
analyses = [analyze_gap(r, company, competitors) for r in st.session_state.audit_results] if has_data else []

if not has_data:
    phase = st.session_state.get('scan_phase', 'hero')

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
            if st.button("🚀 התחל סריקה"):
                st.session_state.scan_phase = 'chat'
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    elif phase == 'chat':
        chat_ph = st.empty()
        run_chat_audit(chat_ph)
        st.session_state.scan_phase = 'done'
        st.rerun()

# ============== EXECUTIVE SUMMARY (CEO-level one-glance card) ==============
def compute_executive_summary(results, analyses, company_name):
    """מחשב מטריקות ברמת מנכ\"ל מתוך תוצאות הסריקה."""
    n_q = len(results)
    if n_q == 0:
        return None
    # סה״כ הזדמנויות = שאלות × מודלים (3)
    total_slots = n_q * 3
    mentions_hits = 0
    for a in analyses:
        for k in ('company_in_openai', 'company_in_gemini', 'company_in_claude'):
            if a.get(k): mentions_hits += 1
    missing_slots = total_slots - mentions_hits

    # Lost Impressions: אומדן ~8K שאילתות חודשיות למודל לכל נושא (שמרני)
    EST_VOL_PER_SLOT = 8000
    lost_impressions = missing_slots * EST_VOL_PER_SLOT

    # Biggest gap: השאלה עם הציון הנמוך
    worst_idx, worst_score = 0, 101
    for i, a in enumerate(analyses):
        if a.get('score', 100) < worst_score:
            worst_score = a.get('score', 100); worst_idx = i
    biggest_gap_q = results[worst_idx]['question'] if worst_idx < len(results) else '—'

    # Quick win: שאלה שבה IDI במקורות אבל לא בתשובה של אף מודל (פשוט לתקן!)
    quick_win_idx = None
    for i, a in enumerate(analyses):
        if a.get('company_in_sources') and not (a.get('company_in_openai') or a.get('company_in_gemini') or a.get('company_in_claude')):
            quick_win_idx = i; break
    quick_win_q = results[quick_win_idx]['question'] if quick_win_idx is not None else None

    # Top competitor — המתחרה הכי דומיננטי על פני כל השאלות
    comp_counter = Counter()
    for a in analyses:
        comp_counter.update(a.get('comp_in_gemini', []))
        comp_counter.update(a.get('comp_in_openai', []))
        comp_counter.update(a.get('comp_in_claude', []) or [])
    top_comp, top_comp_n = (comp_counter.most_common(1)[0] if comp_counter else ('—', 0))

    # Priority action — ה-brief הראשון שנוצר (מתוך השאלה עם הפער הכי חמור שיש לה brief)
    priority_brief = None
    # סדר לפי ציון עולה - גרועות קודם
    sorted_idxs = sorted(range(n_q), key=lambda i: analyses[i].get('score', 100))
    for i in sorted_idxs:
        b = results[i].get('content_brief')
        if b and not b.get('error') and b.get('headline'):
            priority_brief = {
                "question": results[i]['question'],
                "headline": b.get('headline', ''),
                "platform": b.get('recommended_platform', '') or '—',
                "length": b.get('recommended_length', '—'),
            }
            break

    return {
        "n_questions": n_q,
        "avg_score": round(sum(a['score'] for a in analyses) / n_q),
        "mentions_hits": mentions_hits,
        "total_slots": total_slots,
        "missing_slots": missing_slots,
        "lost_impressions": lost_impressions,
        "biggest_gap": biggest_gap_q,
        "biggest_gap_score": worst_score,
        "quick_win": quick_win_q,
        "top_competitor": top_comp,
        "top_competitor_count": top_comp_n,
        "priority_brief": priority_brief,
    }

if has_data:
    exec_sum = compute_executive_summary(st.session_state.audit_results, analyses, company)
    if exec_sum:
        # Number formatting עם פסיקים
        lost_str = f"{exec_sum['lost_impressions']:,}"
        # Priority action HTML
        if exec_sum['priority_brief']:
            pb = exec_sum['priority_brief']
            action_html = f'''
            <div class="qx-exec-action">
                <div class="qx-exec-action-lbl">🎯 Top Priority Action</div>
                <div class="qx-exec-action-headline">{pb['headline']}</div>
                <div class="qx-exec-action-meta">
                    פרסום ב-<code>{pb['platform']}</code> · {pb['length']} מילים<br/>
                    <span style="opacity:.8">בתגובה לשאלה:</span> {pb['question']}
                </div>
            </div>
            '''
        else:
            action_html = f'''
            <div class="qx-exec-action">
                <div class="qx-exec-action-lbl">✅ Status</div>
                <div class="qx-exec-action-headline">נוכחות תקינה — אין צורך בפעולה מיידית</div>
                <div class="qx-exec-action-meta">המשיכו לעקוב אחר מטריקות חודשיות כדי לתחזק מיצוב.</div>
            </div>
            '''
        quick_win_val = exec_sum['quick_win'] or '—'
        quick_win_sub = 'הזדמנות קלה – המקור קיים, רק ה-AI לא בחר להזכיר' if exec_sum['quick_win'] else 'אין quick wins נוכחיים'
        # truncate long question for display
        def _trunc(s, n=48): s = s or '—'; return s if len(s) <= n else s[:n-1] + '…'
        exec_html = f'''
        <div class="qx-exec">
            <div class="qx-exec-head">
                <div class="qx-exec-head-ic">📊</div>
                <div>
                    <div class="qx-exec-head-t">Executive Summary</div>
                    <div class="qx-exec-head-h">סיכום מנכ״ל · {company}</div>
                </div>
                <div class="qx-exec-head-badge">🤖 AI Presence Audit</div>
            </div>
            <div class="qx-exec-body">
                <div class="qx-exec-hero-metric">
                    <div class="qx-exec-hero-lbl">⚠️ Lost Impressions חודשיות</div>
                    <div class="qx-exec-hero-val">{lost_str}</div>
                    <div class="qx-exec-hero-unit">חשיפות פוטנציאליות שהוחמצו</div>
                    <div class="qx-exec-hero-sub">
                        {exec_sum['missing_slots']} מתוך {exec_sum['total_slots']} אפשרויות אזכור<br/>
                        <span style="opacity:.75">(אומדן שמרני: ~8,000 שאילתות חודשיות למודל לנושא)</span>
                    </div>
                </div>
                <div class="qx-exec-kpis">
                    <div class="qx-exec-kpi">
                        <div class="qx-exec-kpi-lbl">🎯 ציון נוכחות כללי</div>
                        <div class="qx-exec-kpi-val">{exec_sum['avg_score']}<span style="opacity:.6;font-size:14px">/100</span></div>
                        <div class="qx-exec-kpi-sub">ממוצע על פני {exec_sum['n_questions']} שאלות</div>
                    </div>
                    <div class="qx-exec-kpi">
                        <div class="qx-exec-kpi-lbl">🔴 הפער הגדול ביותר</div>
                        <div class="qx-exec-kpi-val" style="font-size:14px;line-height:1.4">{_trunc(exec_sum['biggest_gap'], 60)}</div>
                        <div class="qx-exec-kpi-sub">ציון: {exec_sum['biggest_gap_score']}/100</div>
                    </div>
                    <div class="qx-exec-kpi">
                        <div class="qx-exec-kpi-lbl">🏆 מתחרה דומיננטי</div>
                        <div class="qx-exec-kpi-val">{exec_sum['top_competitor']}</div>
                        <div class="qx-exec-kpi-sub">{exec_sum['top_competitor_count']} אזכורים על פני השאילתות</div>
                    </div>
                </div>
                {action_html}
            </div>
        </div>
        '''
        st.markdown(exec_html, unsafe_allow_html=True)

# ============== DASHBOARD: GAUGE + COMPETITORS ==============
avg_score = sum(a["score"] for a in analyses) / len(analyses)
comp_counter = Counter()
for a in analyses:
    comp_counter.update(a["comp_in_gemini"]); comp_counter.update(a["comp_in_openai"]); comp_counter.update(a["comp_in_sources"])

critical_label = "Critical" if avg_score < 40 else ("Medium" if avg_score < 70 else "Strong")
critical_color = "#ED1F4A" if avg_score < 40 else ("#eab308" if avg_score < 70 else "#16a34a")

col_g, col_c = st.columns(2, gap="medium")

with col_g:
    st.markdown(f'''
    <div class="dash-card">
        <div class="card-title">AI Visibility Index: <span class="crit" style="color:{critical_color}">{critical_label}</span></div>
    ''', unsafe_allow_html=True)
    # gauge
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_score,
        number={'suffix': '%', 'font': {'size': 38, 'color': '#0a1a3a', 'family': 'Assistant'}},
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': critical_color, 'thickness': 0.28},
            'bgcolor': '#f0f1f5',
            'borderwidth': 0,
            'shape': 'angular',
        },
        domain={'x': [0, 1], 'y': [0, 1]},
    ))
    gauge.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor='rgba(0,0,0,0)', font=dict(family='Assistant'))
    st.plotly_chart(gauge, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<div class="gauge-label">Low Brand Authority (מדד סמכות נמוך)</div></div>' if avg_score < 40
                else f'<div class="gauge-label">מדד סמכות מותג</div></div>',
                unsafe_allow_html=True)

with col_c:
    st.markdown('<div class="dash-card"><div class="card-title">Competitor Dominance</div>', unsafe_allow_html=True)
    # Build competitor bars - up to 6 (including our company)
    items = comp_counter.most_common(5)
    labels = [c for c, _ in items]
    values = [v for _, v in items]
    # Insert our company
    our_count = sum(1 for a in analyses if a["score"] > 0)
    labels.append(company)
    values.append(our_count)
    # Sort by value desc for display
    pairs = sorted(zip(labels, values), key=lambda x: -x[1])
    colors = ['#0a1a3a' if p[0] == company else '#ED1F4A' for p in pairs]
    x_lbls = [p[0] for p in pairs]
    y_vals = [p[1] for p in pairs]
    bar = go.Figure(go.Bar(
        x=x_lbls, y=y_vals,
        marker=dict(color=colors, cornerradius=6),
        text=[f"{v}" for v in y_vals],
        textposition='outside',
        textfont=dict(color='#6b7280', size=12, family='Assistant'),
    ))
    bar.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=30),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(showgrid=False, tickfont=dict(size=11, color='#6b7280', family='Assistant')),
                      yaxis=dict(showgrid=False, visible=False),
                      showlegend=False, font=dict(family='Assistant'))
    if not pairs or sum(y_vals) == 0:
        bar.add_annotation(text="אין נתונים עדיין", x=0.5, y=0.5, xref='paper', yref='paper',
                           showarrow=False, font=dict(color='#9aa3b2', size=14))
    st.plotly_chart(bar, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ============== TOP CITED SOURCES TABLE (real data) ==============
# אוגר מקורות לפי דומיין: כמה פעמים ציטטו, מי ציטט, האם מזכיר את החברה
feed_rows_html = ""
if has_data:
    dom_stats = {}  # dom -> {"count":int, "by":set, "has_us":bool, "url":str}
    for res in st.session_state.audit_results:
        for s in res.get("sources", []):
            dom = domain_of(s['url'])
            if not dom: continue
            has_us = any(al.lower() in (s.get('title','')+s.get('content','')+s.get('url','')).lower()
                         for al in [company] + COMPANY_ALIASES.get(company, []))
            if dom not in dom_stats:
                dom_stats[dom] = {"count": 0, "by": set(), "has_us": False, "url": s['url']}
            dom_stats[dom]["count"] += 1
            dom_stats[dom]["by"].update(s.get("by", []))
            if has_us: dom_stats[dom]["has_us"] = True

    # מיון: לפי כמות ציטוטים ואז אם מזכיר אותנו
    sorted_doms = sorted(dom_stats.items(), key=lambda x: (-x[1]["count"], -int(x[1]["has_us"])))[:10]

    total_questions = len(st.session_state.audit_results)
    for dom, d in sorted_doms:
        initial = dom[0].upper() if dom else '?'
        # מי ציטט
        by_set = d["by"]
        if len(by_set) >= 3:
            by_html = '<span class="feed-by feed-by-all">🔥 כל השלושה</span>'
        elif len(by_set) == 2:
            icons = []
            if 'gemini' in by_set: icons.append('✨')
            if 'openai' in by_set: icons.append('🧠')
            if 'claude' in by_set: icons.append('🎭')
            by_html = f'<span class="feed-by feed-by-both">{" ".join(icons)} שניים</span>'
        elif 'gemini' in by_set:
            by_html = '<span class="feed-by feed-by-gem">✨ Gemini</span>'
        elif 'openai' in by_set:
            by_html = '<span class="feed-by feed-by-chat">🧠 ChatGPT</span>'
        elif 'claude' in by_set:
            by_html = '<span class="feed-by feed-by-claude">🎭 Claude</span>'
        else:
            by_html = '<span class="feed-by">—</span>'

        # תדירות
        freq_pct = int(100 * d["count"] / max(total_questions, 1))
        freq_html = (f'<div class="feed-freq"><div class="feed-freq-bar">'
                     f'<div class="feed-freq-fill" style="width:{freq_pct}%"></div></div>'
                     f'<span class="feed-freq-txt">{d["count"]}/{total_questions}</span></div>')

        # מזכיר את החברה?
        if d["has_us"]:
            mention_html = '<span class="pill-green">✓ מזכיר</span>'
        else:
            mention_html = '<span class="pill-red">✗ לא מזכיר</span>'

        # פעולה מומלצת
        if d["has_us"]:
            action = "✅ אזכור קיים — שמרו על זה"
            action_cls = "feed-action-ok"
        elif d["count"] >= 2:
            action = "🎯 עדיפות גבוהה — פרסמו כאן"
            action_cls = "feed-action-hot"
        else:
            action = "💡 שקלו יצירת תוכן"
            action_cls = "feed-action-mid"

        feed_rows_html += f"""
        <tr>
            <td><div class="src-cell"><span class="src-avatar">{initial}</span>
                <a href="{d['url']}" target="_blank" style="color:#0a1a3a;text-decoration:none;font-weight:600">{dom}</a></div></td>
            <td>{by_html}</td>
            <td>{freq_html}</td>
            <td>{mention_html}</td>
            <td class="{action_cls}">{action}</td>
        </tr>"""

if not feed_rows_html:
    feed_rows_html = '<tr><td colspan="5" style="text-align:center;color:#9aa3b2;padding:28px">הפעל סריקה כדי לצפות בנתונים</td></tr>'

st.markdown(f"""
<div class="feed-wrap">
    <div class="feed-title">מקורות מובילים ש-AI מצטט · דאטה אמיתית</div>
    <table class="feed">
        <thead>
            <tr>
                <th>דומיין</th><th>ציטט על ידי</th><th>תדירות</th><th>מזכיר את {company}?</th><th>פעולה מומלצת</th>
            </tr>
        </thead>
        <tbody>{feed_rows_html}</tbody>
    </table>
</div>
""", unsafe_allow_html=True)

# ============== RERUN BUTTON ==============
st.markdown("<div style='margin: 24px 0 10px 0'></div>", unsafe_allow_html=True)

# שורת ניהול Baseline + פעולות
if has_data:
    has_baseline = st.session_state.baseline_snapshot is not None
    bcols = st.columns([1.1, 1.3, 1.1, 1, 1, 2])
    with bcols[0]:
        if st.button("🔄 סרוק שוב"):
            st.session_state.audit_results = []
            st.session_state.scan_phase = 'chat'
            st.rerun()
    with bcols[1]:
        if st.button("📸 שמור כ-Baseline", help="שומר את התוצאות הנוכחיות כנקודת השוואה"):
            st.session_state.baseline_snapshot = build_snapshot(
                st.session_state.audit_results, analyses, label="📸 Baseline"
            )
            st.rerun()
    with bcols[2]:
        if st.button("🎬 הדמה 'לפני'", help="יוצר baseline נחות לצורכי דמו — מראה מה היה לפני פרסום ה-brief"):
            current = build_snapshot(st.session_state.audit_results, analyses, label="Current")
            st.session_state.baseline_snapshot = simulate_degraded_baseline(current)
            st.rerun()
    with bcols[3]:
        if has_baseline and st.button("♻️ מחק Baseline"):
            st.session_state.baseline_snapshot = None
            st.rerun()
    with bcols[4]:
        if st.button("🗑️ נקה"):
            st.session_state.audit_results = []
            st.session_state.baseline_snapshot = None
            st.session_state.scan_phase = 'hero'
            st.rerun()

    # ========== BEFORE / AFTER COMPARISON PANEL ==========
    if has_baseline:
        base = st.session_state.baseline_snapshot
        current = build_snapshot(st.session_state.audit_results, analyses, label="Current")

        def _delta_badge(before, after, unit=""):
            diff = (after or 0) - (before or 0)
            if diff > 0:
                return f'<span class="qx-ba-delta qx-ba-delta-up">▲ +{diff}{unit}</span>'
            elif diff < 0:
                return f'<span class="qx-ba-delta qx-ba-delta-dn">▼ {diff}{unit}</span>'
            else:
                return f'<span class="qx-ba-delta qx-ba-delta-flat">— ללא שינוי</span>'

        # Metric 1: Presence Score
        b_score, c_score = base['avg_score'], current['avg_score']
        # Metric 2: total IDI mentions across models
        b_mentions = sum(base['idi_mentions'].values())
        c_mentions = sum(current['idi_mentions'].values())
        # Metric 3: Judge score
        b_j = base.get('avg_judge_score')
        c_j = current.get('avg_judge_score')

        # Per-question rows
        per_q_rows = ""
        bmap = {q['question']: q for q in base['per_question']}
        for cq in current['per_question']:
            bq = bmap.get(cq['question'])
            old_s = bq['score'] if bq else 0
            new_s = cq['score']
            arrow = "▲" if new_s > old_s else ("▼" if new_s < old_s else "—")
            per_q_rows += f'''
            <div class="qx-ba-q-row">
                <div class="qx-ba-q-text">{cq['question']}</div>
                <div class="qx-ba-q-score old">{old_s}</div>
                <div class="qx-ba-arrow">{arrow}</div>
                <div class="qx-ba-q-score new">{new_s}</div>
            </div>
            '''

        judge_row = ""
        if b_j is not None and c_j is not None:
            judge_row = f'''
            <div class="qx-ba-metric">
                <div class="qx-ba-metric-label">🧑‍⚖️ ציון שופט ממוצע</div>
                <div class="qx-ba-metric-row">
                    <span class="qx-ba-before">{b_j}</span>
                    <span class="qx-ba-arrow">→</span>
                    <span class="qx-ba-after">{c_j}</span>
                </div>
                {_delta_badge(b_j, c_j, "/10")}
            </div>
            '''

        ba_html = f'''
        <div class="qx-ba">
            <div class="qx-ba-head">
                <div class="qx-ba-title">🆚 Before / After · השפעת פרסום התוכן</div>
                <div class="qx-ba-sub">{base['label']} · {base['timestamp']} ← Current · {current['timestamp']}</div>
            </div>
            <div class="qx-ba-body">
                <div class="qx-ba-metric">
                    <div class="qx-ba-metric-label">🎯 ציון נוכחות ממוצע</div>
                    <div class="qx-ba-metric-row">
                        <span class="qx-ba-before">{b_score}</span>
                        <span class="qx-ba-arrow">→</span>
                        <span class="qx-ba-after">{c_score}</span>
                    </div>
                    {_delta_badge(b_score, c_score, " נק'")}
                </div>
                <div class="qx-ba-metric">
                    <div class="qx-ba-metric-label">💬 אזכורי ביטוח ישיר (סה״כ)</div>
                    <div class="qx-ba-metric-row">
                        <span class="qx-ba-before">{b_mentions}</span>
                        <span class="qx-ba-arrow">→</span>
                        <span class="qx-ba-after">{c_mentions}</span>
                    </div>
                    {_delta_badge(b_mentions, c_mentions, " אזכורים")}
                </div>
                {judge_row}
            </div>
            <div class="qx-ba-per-q">
                <div class="qx-ba-per-q-title">📊 שינוי לכל שאלה</div>
                {per_q_rows}
            </div>
        </div>
        '''
        st.markdown(ba_html, unsafe_allow_html=True)
else:
    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
    with col_btn1:
        if st.button("🔄 סרוק שוב"):
            st.session_state.audit_results = []
            st.session_state.scan_phase = 'chat'
            st.rerun()
    with col_btn2:
        if st.button("🗑️ נקה תוצאות"):
            st.session_state.audit_results = []
            st.session_state.scan_phase = 'hero'
            st.rerun()

# ============== DETAILED QUESTION RESULTS (PREMIUM) ==============
def _score_ring(score, size=74):
    """SVG circular progress ring."""
    r = 30; c = 2 * 3.14159 * r
    pct = max(0, min(100, score)) / 100
    dash = c * pct
    color = "#ED1F4A" if score < 40 else ("#eab308" if score < 70 else "#16a34a")
    return f'''<div class="qx-score-ring">
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
            <circle cx="{size/2}" cy="{size/2}" r="{r}" stroke="#f0f1f5" stroke-width="7" fill="none"/>
            <circle cx="{size/2}" cy="{size/2}" r="{r}" stroke="{color}" stroke-width="7" fill="none"
                    stroke-dasharray="{dash:.1f} {c-dash:.1f}" stroke-linecap="round"/>
        </svg>
        <div class="qx-score-ring-txt">
            <div class="qx-score-val">{score}</div>
            <div class="qx-score-lbl">SCORE</div>
        </div>
    </div>'''

if has_data:
    st.markdown('<div class="page-title" style="margin-top:36px">🔬 ניתוח מפורט לכל שאילתה</div>', unsafe_allow_html=True)

    for idx, (res, gap) in enumerate(zip(st.session_state.audit_results, analyses), 1):
        # Tags
        meta_tags = []
        if gap["score"] > 0:
            meta_tags.append(f'<span class="qx-tag qx-tag-in">✓ {company} מופיע</span>')
        else:
            meta_tags.append(f'<span class="qx-tag qx-tag-out">✗ {company} חסר</span>')
        n_src = len(res.get('sources', []))
        meta_tags.append(f'<span class="qx-tag qx-tag-score">📚 {n_src} מקורות</span>')
        comp_set = set(gap["comp_in_gemini"] + gap["comp_in_openai"] + gap["comp_in_sources"])
        for c in list(comp_set)[:4]:
            meta_tags.append(f'<span class="qx-tag qx-tag-comp">⚔ {c}</span>')
        meta_html = "".join(meta_tags)

        # Header
        header_html = f'''
        <div class="qx-card">
            <div class="qx-header">
                <div class="qx-index">{idx:02d}</div>
                <div class="qx-header-body">
                    <div class="qx-question">{res["question"]}</div>
                    <div class="qx-meta">{meta_html}</div>
                </div>
                {_score_ring(gap["score"])}
            </div>
        '''
        st.markdown(header_html + '<div class="qx-section">תשובות מה-AI</div>', unsafe_allow_html=True)

        # AI answers
        chat_status = "נמצא ✓" if gap["company_in_openai"] else "חסר ✗"
        gem_status  = "נמצא ✓" if gap["company_in_gemini"] else "חסר ✗"
        claude_status = "נמצא ✓" if gap.get("company_in_claude") else "חסר ✗"
        chat_txt = format_ai_text(res.get('openai', '') or '')
        gem_txt  = format_ai_text(res.get('gemini', '') or '')
        claude_txt = format_ai_text(res.get('claude', '') or '')

        ai_html = f'''
        <div class="qx-ai-grid">
            <div class="qx-ai qx-ai-chat">
                <div class="qx-ai-head">
                    <div class="qx-ai-head-left">
                        <div class="qx-ai-logo">🧠</div>
                        <div>ChatGPT · OpenAI</div>
                    </div>
                    <span class="qx-ai-status">{chat_status}</span>
                </div>
                <div class="qx-ai-body">{chat_txt}</div>
            </div>
            <div class="qx-ai qx-ai-gem">
                <div class="qx-ai-head">
                    <div class="qx-ai-head-left">
                        <div class="qx-ai-logo">✨</div>
                        <div>Gemini · Google</div>
                    </div>
                    <span class="qx-ai-status">{gem_status}</span>
                </div>
                <div class="qx-ai-body">{gem_txt}</div>
            </div>
            <div class="qx-ai qx-ai-claude">
                <div class="qx-ai-head">
                    <div class="qx-ai-head-left">
                        <div class="qx-ai-logo">🎭</div>
                        <div>Claude · Anthropic</div>
                    </div>
                    <span class="qx-ai-status">{claude_status}</span>
                </div>
                <div class="qx-ai-body">{claude_txt}</div>
            </div>
        </div>
        '''
        st.markdown(ai_html, unsafe_allow_html=True)

        # =============== CROSS-MODEL JUDGMENT (Claude as Judge) ===============
        judgments = res.get('judgments') or {}
        valid_judgments = [(k, v) for k, v in judgments.items() if v and not v.get('error')]
        if valid_judgments:
            model_display = {
                "openai": ("🧠", "ChatGPT"),
                "gemini": ("✨", "Gemini"),
                "claude": ("🎭", "Claude (עצמי)"),
            }
            judge_cards_html = ""
            for model_key, j in valid_judgments:
                icon, name = model_display.get(model_key, ("🤖", model_key))
                score = int(j.get('score', 0) or 0)
                score_cls = "qx-judge-score-hi" if score >= 8 else ("qx-judge-score-mid" if score >= 5 else "qx-judge-score-lo")
                bias = j.get('bias_detected')
                idi_src = j.get('idi_in_sources')
                idi_ans = j.get('idi_in_answer')
                dom_brand = j.get('dominant_brand') or '—'
                verdict = j.get('verdict', '') or ''
                fix = j.get('fix_recommendation', '') or ''

                flags = []
                if bias:
                    flags.append('<span class="qx-judge-flag qx-judge-flag-bias">⚠️ הטיה</span>')
                else:
                    flags.append('<span class="qx-judge-flag qx-judge-flag-fair">✓ הוגן</span>')
                if idi_src is True:
                    flags.append('<span class="qx-judge-flag qx-judge-flag-src">ביטוח ישיר במקורות</span>')
                if idi_ans is True:
                    flags.append('<span class="qx-judge-flag qx-judge-flag-fair">מוזכרת בתשובה</span>')
                elif idi_src is True and idi_ans is False:
                    flags.append('<span class="qx-judge-flag qx-judge-flag-ans">הושמטה מהתשובה!</span>')
                flags_html = "".join(flags)

                judge_cards_html += f'''
                <div class="qx-judge-card">
                    <div class="qx-judge-card-head">
                        <div class="qx-judge-model">{icon} {name}</div>
                        <div class="qx-judge-score {score_cls}">{score}/10</div>
                    </div>
                    <div class="qx-judge-flags">{flags_html}</div>
                    <div class="qx-judge-dom">מותג דומיננטי: <b>{dom_brand}</b></div>
                    <div class="qx-judge-verdict">{verdict}</div>
                    <div class="qx-judge-fix"><b>💡 המלצה:</b> {fix}</div>
                </div>
                '''

            judge_html = f'''
            <div class="qx-judge-section">
                <div class="qx-judge-title">
                    🧑‍⚖️ שיפוט צולב · ביקורת אובייקטיבית של התשובות
                    <span class="qx-judge-badge">🎭 Claude = Judge</span>
                </div>
                <div class="qx-judge-grid">{judge_cards_html}</div>
            </div>
            '''
            st.markdown(judge_html, unsafe_allow_html=True)

        # =============== CONTENT BRIEF (Actionable deliverable) ===============
        brief = res.get('content_brief')
        if brief and not brief.get('error'):
            headline = brief.get('headline', '') or ''
            meta_desc = brief.get('meta_description', '') or ''
            outline = brief.get('outline', []) or []
            keywords = brief.get('target_keywords', []) or []
            length = brief.get('recommended_length', '—')
            platform = brief.get('recommended_platform', '') or '—'
            platform_reason = brief.get('platform_reason', '') or ''
            key_args = brief.get('key_arguments', []) or []
            unique_angle = brief.get('unique_angle', '') or ''
            cta = brief.get('cta', '') or ''
            expected_impact = brief.get('expected_impact', '') or ''

            outline_html = "".join(f"<li>{h}</li>" for h in outline)
            kw_html = "".join(f'<span class="qx-brief-kw-chip">#{k}</span>' for k in keywords)
            args_html = "".join(f"<li>{a}</li>" for a in key_args)

            brief_html = f'''
            <div class="qx-brief">
                <div class="qx-brief-head">
                    📝 Content Brief · מוכן לצוות תוכן
                    <span class="qx-brief-head-badge">🎭 מיוצר על ידי Claude</span>
                </div>
                <div class="qx-brief-body">
                    <div class="qx-brief-h1">{headline}</div>
                    <div class="qx-brief-meta">📝 <b>Meta:</b> {meta_desc}</div>

                    <div class="qx-brief-grid">
                        <div class="qx-brief-box">
                            <div class="qx-brief-box-title">📋 מבנה המאמר (Outline)</div>
                            <ol class="qx-brief-outline">{outline_html}</ol>
                        </div>
                        <div class="qx-brief-box">
                            <div class="qx-brief-box-title">🎯 מילות מפתח</div>
                            <div class="qx-brief-kw">{kw_html}</div>
                            <div class="qx-brief-stat-row" style="margin-top:14px">
                                <span class="qx-brief-stat-key">📏 אורך:</span>
                                <span class="qx-brief-stat-val">{length} מילים</span>
                            </div>
                            <div class="qx-brief-platform">
                                <div style="font-size:11px;opacity:.9;margin-bottom:4px">📍 לפרסם ב:</div>
                                <div class="qx-brief-platform-dom">{platform}</div>
                                <div class="qx-brief-platform-reason">{platform_reason}</div>
                            </div>
                        </div>
                    </div>

                    <div class="qx-brief-box">
                        <div class="qx-brief-box-title">💪 טיעוני מפתח לשילוב</div>
                        <ul class="qx-brief-args">{args_html}</ul>
                    </div>

                    <div class="qx-brief-angle">
                        <span class="qx-brief-angle-label">✨ זווית ייחודית</span>
                        {unique_angle}
                    </div>

                    <div class="qx-brief-impact">
                        <div class="qx-brief-impact-icon">🚀</div>
                        <div><b>למה זה צפוי לעבוד:</b> {expected_impact}</div>
                    </div>

                    <div class="qx-brief-cta">📣 {cta}</div>
                </div>
            </div>
            '''
            st.markdown(brief_html, unsafe_allow_html=True)

        # Thinking panels
        gem_think = res.get('gemini_thinking', '')
        chat_think = res.get('openai_thinking', '')
        chat_queries = res.get('openai_search_queries', []) or []

        if chat_queries:
            queries_html = "".join(f'<span class="qx-think-query">🔍 {q}</span>' for q in chat_queries)
            st.markdown(
                f'<details class="qx-think" open><summary>🔍 שאילתות חיפוש ש-ChatGPT בנה ({len(chat_queries)})</summary>'
                f'<div class="qx-think-body"><div class="qx-think-queries">{queries_html}</div></div></details>',
                unsafe_allow_html=True
            )

        if chat_think and 'fallback' not in chat_think:
            st.markdown(
                f'<details class="qx-think"><summary>🧠 תהליך החשיבה של ChatGPT (o4-mini)</summary>'
                f'<div class="qx-think-body">{format_ai_text(chat_think)}</div></details>',
                unsafe_allow_html=True
            )

        if gem_think:
            st.markdown(
                f'<details class="qx-think"><summary>✨ תהליך החשיבה של Gemini</summary>'
                f'<div class="qx-think-body">{format_ai_text(gem_think)}</div></details>',
                unsafe_allow_html=True
            )

        # Claude thinking + search queries
        claude_queries = res.get('claude_search_queries', []) or []
        claude_think = res.get('claude_thinking', '')
        if claude_queries:
            cq_html = "".join(f'<span class="qx-think-query">🔍 {q}</span>' for q in claude_queries)
            st.markdown(
                f'<details class="qx-think" open><summary>🔍 שאילתות חיפוש ש-Claude בנה ({len(claude_queries)})</summary>'
                f'<div class="qx-think-body"><div class="qx-think-queries">{cq_html}</div></div></details>',
                unsafe_allow_html=True
            )
        if claude_think:
            st.markdown(
                f'<details class="qx-think"><summary>🎭 תהליך החשיבה של Claude</summary>'
                f'<div class="qx-think-body">{format_ai_text(claude_think)}</div></details>',
                unsafe_allow_html=True
            )

        # Sources – real citations from each AI model
        if res['sources']:
            n_gem = len(res.get('gemini_sources', []))
            n_cht = len(res.get('openai_sources', []))
            n_cld = len(res.get('claude_sources', []))
            st.markdown(
                f'<div class="qx-section">ציטוטים שה-AI השתמש בהם · '
                f'<span style="color:#be185d">Gemini {n_gem}</span> · '
                f'<span style="color:#1e40af">ChatGPT {n_cht}</span> · '
                f'<span style="color:#b45309">Claude {n_cld}</span></div>',
                unsafe_allow_html=True
            )

            src_html = '<div class="qx-src-grid">'
            for s in res['sources']:
                dom = domain_of(s['url'])
                has_us = any(al.lower() in (s.get('title','')+s.get('content','')+s.get('url','')).lower()
                             for al in [company] + COMPANY_ALIASES.get(company, []))
                title = (s.get('title') or dom)[:75]
                if len(s.get('title') or '') > 75: title += "…"
                favicon = f"https://www.google.com/s2/favicons?domain={dom}&sz=64"
                by = s.get('by', [])
                if len(by) >= 3:
                    by_tag = '<span class="qx-src-by qx-src-by-all">🔥 כל השלושה</span>'
                elif len(by) == 2:
                    # מציג את שני התגים
                    tags = []
                    if 'gemini' in by: tags.append('<span class="qx-src-by qx-src-by-gem">✨</span>')
                    if 'openai' in by: tags.append('<span class="qx-src-by qx-src-by-chat">🧠</span>')
                    if 'claude' in by: tags.append('<span class="qx-src-by qx-src-by-claude">🎭</span>')
                    by_tag = " ".join(tags)
                elif 'gemini' in by:
                    by_tag = '<span class="qx-src-by qx-src-by-gem">✨ Gemini</span>'
                elif 'openai' in by:
                    by_tag = '<span class="qx-src-by qx-src-by-chat">🧠 ChatGPT</span>'
                elif 'claude' in by:
                    by_tag = '<span class="qx-src-by qx-src-by-claude">🎭 Claude</span>'
                else:
                    by_tag = ''
                cls = "qx-src qx-src-us" if has_us else "qx-src"
                src_html += f'''
                <a href="{s["url"]}" target="_blank" class="{cls}">
                    <div class="qx-src-favicon"><img src="{favicon}" alt=""/></div>
                    <div class="qx-src-body">
                        <div class="qx-src-title">{title}</div>
                        <div class="qx-src-meta">
                            <span>{dom}</span>
                            {by_tag}
                        </div>
                    </div>
                </a>'''
            src_html += '</div>'
            st.markdown(src_html, unsafe_allow_html=True)

        # Recommendation
        rec_type, rec_text = build_recommendation(gap, company, res['question'])
        is_ok = (rec_type == "success")
        rec_icon = "✓" if is_ok else "💡"
        rec_title = "החברה נוכחת במודעות ה-AI" if is_ok else "זוהה פער – המלצת פעולה"
        rec_cls = "qx-rec qx-rec-ok" if is_ok else "qx-rec"
        rec_html = f'''
        <div class="{rec_cls}">
            <div class="qx-rec-head">
                <div class="qx-rec-head-icon">{rec_icon}</div>
                <div>{rec_title}</div>
            </div>
            <div class="qx-rec-body">{rec_text}</div>
        </div>
        </div>
        '''  # closes .qx-card
        st.markdown(rec_html, unsafe_allow_html=True)
        st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)
