import re
from datetime import datetime
from collections import Counter

# ============== DATA & CONFIGURATION ==============

DEFAULT_COMPANY = "ביטוח ישיר"

DEFAULT_COMPETITORS = [
    "הראל", "מגדל", "מנורה", "כלל", "הפניקס", 
    "איילון", "שומרה", "AIG", "הכשרה", "שירביט"
]

COMPANY_ALIASES = {
    "ביטוח ישיר": ["ביטוח ישיר", "ביטוח-ישיר", "9 מיליון", "ישיר"]
}

# השמה למשתנים גלובליים לשימוש בשאר חלקי האפליקציה
company = DEFAULT_COMPANY
competitors = DEFAULT_COMPETITORS

# ============== ANALYSIS FUNCTIONS ==============

def detect_mentions(text, names, aliases_map=None):
    """זיהוי אזכורי מותגים בטקסט כולל שמות חלופיים."""
    if not text: return []
    found, text_low = [], text.lower()
    for name in names:
        candidates = [name] + (aliases_map.get(name, []) if aliases_map else [])
        for alias in candidates:
            if alias.lower() in text_low:
                found.append(name)
                break
    return found

def domain_of(url):
    """חילוץ שם דומיין נקי מתוך URL."""
    m = re.search(r"https?://([^/]+)/?", url or "")
    return m.group(1).replace("www.", "") if m else (url or "")

def analyze_gap(res, company, competitors):
    """ניתוח פערים לשאילתה בודדת על פני כל המודלים והמקורות."""
    gtxt = res.get("gemini", "") or ""
    otxt = res.get("openai", "") or ""
    ctxt = res.get("claude", "") or ""
    
    # איחוד כל הטקסט מהמקורות לבדיקת אזכורים
    stxt = " ".join([
        (s.get("title","") + " " + s.get("content","") + " " + s.get("url","")) 
        for s in res.get("sources", [])
    ])
    
    # בדיקת נוכחות החברה שלנו
    cg = bool(detect_mentions(gtxt, [company], COMPANY_ALIASES))
    co = bool(detect_mentions(otxt, [company], COMPANY_ALIASES))
    cc = bool(detect_mentions(ctxt, [company], COMPANY_ALIASES))
    cs = bool(detect_mentions(stxt, [company], COMPANY_ALIASES))
    
    # בדיקת נוכחות מתחרים
    comp_g = detect_mentions(gtxt, competitors)
    comp_o = detect_mentions(otxt, competitors)
    comp_c = detect_mentions(ctxt, competitors)
    comp_s = detect_mentions(stxt, competitors)
    
    doms = [domain_of(s["url"]) for s in res.get("sources", [])]
    
    # חישוב ציון ויזביליטי: כל מודל 25% + מקורות 25% = 100%
    score = (25 if cg else 0) + (25 if co else 0) + (25 if cc else 0) + (25 if cs else 0)
    
    return {
        "company_in_gemini": cg, "company_in_openai": co, "company_in_claude": cc,
        "company_in_sources": cs,
        "comp_in_gemini": comp_g, "comp_in_openai": comp_o, "comp_in_claude": comp_c,
        "comp_in_sources": comp_s,
        "source_domains": doms, "score": score
    }

def build_snapshot(results, analyses, label="Current"):
    """בונה תמונת מצב מתומצתת כולל ניתוח דומיינים לפי מודלים (Model Authority)."""
    if not results:
        return None
    
    per_q = []
    idi_mentions = {"openai": 0, "gemini": 0, "claude": 0}
    idi_in_sources_count = 0
    judge_scores = []
    
    # מילון לצבירת נתונים על דומיינים לאורך כל הסריקה
    domain_stats = {}
    
    for r, g in zip(results, analyses):
        # ספירת אזכורי מותג במודלים
        if g.get('company_in_openai'): idi_mentions['openai'] += 1
        if g.get('company_in_gemini'): idi_mentions['gemini'] += 1
        if g.get('company_in_claude'): idi_mentions['claude'] += 1
        if g.get('company_in_sources'): idi_in_sources_count += 1
        
        # איסוף ציוני שופט
        for j in (r.get('judgments') or {}).values():
            if j and not j.get('error') and j.get('score') is not None:
                try: judge_scores.append(int(j['score']))
                except: pass
        
        # --- לוגיקת דומיינים חדשה: בכמה מודלים האתר הופיע ---
        for src in r.get('sources', []):
            dom = domain_of(src.get('url', ''))
            if not dom: continue
            
            if dom not in domain_stats:
                domain_stats[dom] = {
                    "mentions": 0, 
                    "unique_models": set(), 
                    "has_company": False
                }
            
            domain_stats[dom]["mentions"] += 1
            # הוספת המודלים שתייגו את המקור הזה (מתוך פונקציית merge_sources)
            for model_tag in src.get('by', []):
                domain_stats[dom]["unique_models"].add(model_tag)
            
            # בדיקה אם הדומיין אי פעם הזכיר את החברה שלנו
            if not domain_stats[dom]["has_company"]:
                text_to_check = (src.get('title','') + " " + src.get('url','')).lower()
                if company.lower() in text_to_check:
                    domain_stats[dom]["has_company"] = True

        per_q.append({
            "question": r.get('question',''),
            "score": g.get('score', 0),
            "idi_openai": g.get('company_in_openai', False),
            "idi_gemini": g.get('company_in_gemini', False),
            "idi_claude": g.get('company_in_claude', False),
            "idi_in_sources": g.get('company_in_sources', False),
        })

    # עיבוד רשימת הדומיינים לטבלה
    top_domains_table = []
    for dom, stats in domain_stats.items():
        n_models = len(stats["unique_models"])
        top_domains_table.append({
            "domain": dom,
            "model_count": f"{n_models}/3",           # הטקסט שיוצג
            "bar_score": (n_models / 3) * 100,       # אחוז מילוי הפס
            "mentions": stats["mentions"],
            "has_company": stats["has_company"]
        })
    
    # מיון לפי כמות מודלים ואז לפי כמות ציטוטים
    top_domains_table = sorted(top_domains_table, key=lambda x: (x['bar_score'], x['mentions']), reverse=True)
        
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
        "top_domains": top_domains_table[:10] # שומרים את ה-10 המובילים
    }

def simulate_degraded_baseline(snapshot):
    """יוצר baseline 'לפני' ע״י הורדה סימולטיבית של הנתונים — לצורכי דמו."""
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

def build_recommendation(gap, company, question):
    """מייצר המלצה טקסטואלית קצרה על בסיס הפער שזוהה."""
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

def merge_sources(gemini_sources, openai_sources, claude_sources=None):
    """איחוד רשימות מקורות לפי URL (dedup), עם תיוג מי ציטט כל מקור."""
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

    # Biggest gap: השאלה עם הציון הנמוך ביותר
    worst_idx, worst_score = 0, 101
    for i, a in enumerate(analyses):
        if a.get('score', 100) < worst_score:
            worst_score = a.get('score', 100)
            worst_idx = i
    biggest_gap_q = results[worst_idx]['question'] if worst_idx < len(results) else '—'

    # Quick win: שאלה שבה IDI במקורות אבל לא בתשובה של אף מודל
    quick_win_idx = None
    for i, a in enumerate(analyses):
        if a.get('company_in_sources') and not (a.get('company_in_openai') or a.get('company_in_gemini') or a.get('company_in_claude')):
            quick_win_idx = i
            break
    quick_win_q = results[quick_win_idx]['question'] if quick_win_idx is not None else None

    # Top competitor — המתחרה הכי דומיננטי על פני כל השאלות
    comp_counter = Counter()
    for a in analyses:
        comp_counter.update(a.get('comp_in_gemini', []))
        comp_counter.update(a.get('comp_in_openai', []))
        comp_counter.update(a.get('comp_in_claude', []) or [])
    top_comp, top_comp_n = (comp_counter.most_common(1)[0] if comp_counter else ('—', 0))

    # Priority action — ה-brief הראשון שנוצר (מהפער הכי חמור)
    priority_brief = None
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