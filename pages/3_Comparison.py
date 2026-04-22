import streamlit as st
from utils.analysts import analyze_gap, build_snapshot, company, competitors
from components.style import apply_custom_css
from components.ui_utils import load_sidebar, load_top_bar

# ============== הגדרות מעטפת ==============
apply_custom_css()
load_sidebar()
load_top_bar()

# ============== בדיקת נתונים ==============
has_data = bool(st.session_state.get('audit_results'))
has_baseline = st.session_state.get('baseline_snapshot') is not None

if not has_data:
    st.info("לא נמצאו נתונים להשוואה. אנא בצע סריקה בעמוד הבית.")
    st.stop()

# הכנת האנליזה הנוכחית לחישובים
results = st.session_state.audit_results
analyses = [analyze_gap(r, company, competitors) for r in results]

# ============== כותרת העמוד ==============
st.markdown('<div class="page-title" style="margin-top:36px">🆚 השוואת ביצועים ושיפור</div>', unsafe_allow_html=True)

# ============== לוגיקת השוואה (Before / After) ==============
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
    # ============== הודעה וכפתורי ניהול כשאין Baseline ==============
    st.warning("לא הוגדר Baseline להשוואה. שמור את התוצאות הנוכחיות כ-Baseline בעמוד הדשבורד כדי לראות שיפור לאורך זמן.")
    
    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
    with col_btn1:
        if st.button("🔄 סרוק שוב"):
            st.session_state.audit_results = []
            st.session_state.scan_phase = 'chat'
            st.switch_page("app.py")
    with col_btn2:
        if st.button("🗑️ נקה תוצאות"):
            st.session_state.audit_results = []
            st.session_state.baseline_snapshot = None
            st.session_state.scan_phase = 'hero'
            st.switch_page("app.py")