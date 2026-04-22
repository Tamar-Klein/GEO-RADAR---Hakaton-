import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import Counter

from utils.analysts import (
    analyze_gap, compute_executive_summary, domain_of, 
    build_snapshot, simulate_degraded_baseline, 
    company, competitors, COMPANY_ALIASES
)
from components.style import apply_custom_css
from components.ui_utils import load_sidebar, load_top_bar

# החלת עיצוב ותפריטים
apply_custom_css()
load_sidebar()
load_top_bar()

# בדיקת קיום נתונים ב-Session State
has_data = bool(st.session_state.get('audit_results'))

if has_data:
    results = st.session_state.audit_results
    analyses = [analyze_gap(r, company, competitors) for r in results]
    
    # חישוב סיכום מנהלים
    exec_sum = compute_executive_summary(results, analyses, company)
    
    if exec_sum:
        # פורמט מספרים עם פסיקים
        lost_str = f"{exec_sum['lost_impressions']:,}"
        
        # בניית HTML עבור פעולה בעדיפות עליונה
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
        
        # פונקציית עזר לקיצור טקסט ארוך
        def _trunc(s, n=48): 
            s = s or '—'
            return s if len(s) <= n else s[:n-1] + '…'
            
        # ============== EXECUTIVE SUMMARY HTML ==============
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
        comp_counter.update(a["comp_in_gemini"])
        comp_counter.update(a["comp_in_openai"])
        comp_counter.update(a["comp_in_sources"])

    critical_label = "Critical" if avg_score < 40 else ("Medium" if avg_score < 70 else "Strong")
    critical_color = "#ED1F4A" if avg_score < 40 else ("#eab308" if avg_score < 70 else "#16a34a")

    col_g, col_c = st.columns(2, gap="medium")

    with col_g:
        st.markdown(f'''
        <div class="dash-card">
            <div class="card-title">AI Visibility Index: <span class="crit" style="color:{critical_color}">{critical_label}</span></div>
        ''', unsafe_allow_html=True)
        
        # Gauge Chart
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
        
        st.markdown(f'<div class="gauge-label">{"Low Brand Authority (מדד סמכות נמוך)" if avg_score < 40 else "מדד סמכות מותג"}</div></div>',
                    unsafe_allow_html=True)

    with col_c:
        st.markdown('<div class="dash-card"><div class="card-title">Competitor Dominance</div>', unsafe_allow_html=True)
        
        items = comp_counter.most_common(5)
        labels = [c for c, _ in items]
        values = [v for _, v in items]
        
        # הוספת החברה שלנו להשוואה
        our_count = sum(1 for a in analyses if a["score"] > 0)
        labels.append(company)
        values.append(our_count)
        
        # מיון להצגה
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
        
    # ============== TOP CITED SOURCES TABLE ==============
    feed_rows_html = ""
    dom_stats = {}
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

    sorted_doms = sorted(dom_stats.items(), key=lambda x: (-x[1]["count"], -int(x[1]["has_us"])))[:10]
    total_questions = len(st.session_state.audit_results)

    for dom, d in sorted_doms:
        initial = dom[0].upper() if dom else '?'
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

        freq_pct = int(100 * d["count"] / max(total_questions, 1))
        freq_html = (f'<div class="feed-freq"><div class="feed-freq-bar">'
                     f'<div class="feed-freq-fill" style="width:{freq_pct}%"></div></div>'
                     f'<span class="feed-freq-txt">{d["count"]}/{total_questions}</span></div>')

        if d["has_us"]:
            mention_html = '<span class="pill-green">✓ מזכיר</span>'
            action = "✅ אזכור קיים — שמרו על זה"
            action_cls = "feed-action-ok"
        else:
            mention_html = '<span class="pill-red">✗ לא מזכיר</span>'
            if d["count"] >= 2:
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

    # ============== RERUN & BASELINE BUTTONS ==============
    st.markdown("<div style='margin: 24px 0 10px 0'></div>", unsafe_allow_html=True)

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
        if st.button("🎬 הדמה 'לפני'", help="יוצר baseline נחות לצורכי דמו"):
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
else:
    st.info("לא נמצאו נתונים להצגה. אנא בצע סריקה בעמוד הראשי.")


   