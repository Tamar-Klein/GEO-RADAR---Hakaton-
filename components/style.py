import streamlit as st

def apply_custom_css():
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