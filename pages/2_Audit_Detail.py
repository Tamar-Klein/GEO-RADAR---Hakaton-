import streamlit as st
from utils.analysts import analyze_gap, domain_of, build_recommendation, company, competitors, COMPANY_ALIASES
from components.style import apply_custom_css
from components.ui_utils import load_sidebar, load_top_bar, format_ai_text

# ============== הגדרות מעטפת ==============
apply_custom_css()
load_sidebar()
load_top_bar()

# ============== פונקציות עזר ויזואליות ==============
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

# ============== בדיקת נתונים ==============
has_data = bool(st.session_state.get('audit_results'))

if not has_data:
    st.info("לא נמצאו נתונים להצגה. אנא בצע סריקה בעמוד הראשי.")
    st.stop()

# הכנת האנליזה
results = st.session_state.audit_results
analyses = [analyze_gap(r, company, competitors) for r in results]

# ============== כותרת העמוד ==============
st.markdown('<div class="page-title" style="margin-top:36px">🔬 ניתוח מפורט לכל שאילתה</div>', unsafe_allow_html=True)

# ============== לולאת השאלות המרכזית ==============
for idx, (res, gap) in enumerate(zip(results, analyses), 1):
    
    # --- Tags ---
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

    # --- Header ---
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

    # --- AI answers ---
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

    # --- Sources & Citations ---
    if res.get('sources'):
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

    # --- Thinking Panels: Claude ---
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

    # --- Thinking Panels: GPT & Gemini ---
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

    # --- Content Brief ---
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

    # --- Cross-Model Judgment ---
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
            if bias: flags.append('<span class="qx-judge-flag qx-judge-flag-bias">⚠️ הטיה</span>')
            else: flags.append('<span class="qx-judge-flag qx-judge-flag-fair">✓ הוגן</span>')
            
            if idi_src is True: flags.append('<span class="qx-judge-flag qx-judge-flag-src">ביטוח ישיר במקורות</span>')
            
            if idi_ans is True: flags.append('<span class="qx-judge-flag qx-judge-flag-fair">מוזכרת בתשובה</span>')
            elif idi_src is True and idi_ans is False: flags.append('<span class="qx-judge-flag qx-judge-flag-ans">הושמטה מהתשובה!</span>')
            
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

    # --- Recommendation ---
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
    ''' # הסגירה האחרונה היא ל-qx-card
    st.markdown(rec_html, unsafe_allow_html=True)
    st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)