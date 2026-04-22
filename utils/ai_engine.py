import os
import re
import ssl
import time
import json as _json
import httpx
import streamlit as st
from openai import OpenAI
from google import genai
from google.genai import types as genai_types
from dotenv import load_dotenv

# ייבוא פונקציות עזר מהמודולים האחרים
from utils.analysts import domain_of, merge_sources, detect_mentions, DEFAULT_COMPANY, DEFAULT_COMPETITORS, COMPANY_ALIASES
from components.ui_utils import _bubble_user, _bubble_ai_typing, _bubble_ai_done, format_ai_text

from utils.prompts import (
    JUDGE_SYSTEM_PROMPT, 
    BRAND_AUDIT_SYSTEM_PROMPT, 
    CONTENT_BRIEF_SYSTEM_PROMPT
)

# הגדרות SSL לעבודה מול ה-APIs
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()

# Anthropic (Claude) - טעינה אופציונלית
try:
    from anthropic import Anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    Anthropic = None
    _ANTHROPIC_AVAILABLE = False

# ============== הגדרות קבועות ==============

FIXED_QUESTIONS = [
    "איזה ביטוח רכב הכי מומלץ לנהג צעיר?"
    
]
# "מי חברת הביטוח עם הדירוג הכי גבוה בשירות לקוחות?",
#     "מהם היתרונות של ביטוח בריאות פרטי על פני שב״ן?",
#     "איזה ביטוח נסיעות לחו״ל מומלץ לתרמילאים?",
t_key = os.getenv("TAVILY_API_KEY", "")
g_key = os.getenv("GOOGLE_API_KEY", "")
o_key = os.getenv("OPENAI_API_KEY", "")
a_key = os.getenv("ANTHROPIC_API_KEY", "")

company = DEFAULT_COMPANY
competitors = DEFAULT_COMPETITORS

# ============== פונקציות חילוץ נתונים (Extraction) ==============

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

def extract_openai_responses(response):
    """חילוץ תשובה + מקורות + reasoning מ-OpenAI Responses API"""
    answer = ""
    sources = []
    thinking = ""
    search_queries = []
    try:
        answer = getattr(response, 'output_text', '') or ''
        output = getattr(response, 'output', None) or []
        for item in output:
            itype = getattr(item, 'type', None) or (item.get('type') if isinstance(item, dict) else None)
            if itype == 'reasoning':
                summaries = getattr(item, 'summary', None) or (item.get('summary') if isinstance(item, dict) else []) or []
                for s in summaries:
                    txt = getattr(s, 'text', None) or (s.get('text') if isinstance(s, dict) else '')
                    if txt: thinking += (("\n\n" if thinking else "") + txt)
            elif itype == 'web_search_call':
                action = getattr(item, 'action', None) or (item.get('action') if isinstance(item, dict) else None)
                if action:
                    q = getattr(action, 'query', None) or (action.get('query') if isinstance(action, dict) else None)
                    if q: search_queries.append(q)
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
            if btype == 'thinking':
                t = getattr(block, 'thinking', '') or ''
                if t: thinking += (("\n\n" if thinking else "") + t)
            elif btype == 'server_tool_use':
                name = getattr(block, 'name', None)
                if name == 'web_search':
                    inp = getattr(block, 'input', None) or {}
                    q = inp.get('query') if isinstance(inp, dict) else getattr(inp, 'query', None)
                    if q: search_queries.append(q)
            elif btype == 'web_search_tool_result':
                results = getattr(block, 'content', None) or []
                for r in results:
                    if getattr(r, 'type', None) != 'web_search_result': continue
                    url = getattr(r, 'url', '') or ''
                    title = getattr(r, 'title', '') or ''
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        sources.append({"title": title or url, "url": url, "content": ""})
            elif btype == 'text':
                txt = getattr(block, 'text', '') or ''
                if txt: answer_parts.append(txt)
        answer = "\n".join(answer_parts).strip()
    except Exception:
        answer = ""
    return answer, sources, thinking, search_queries

# ============== פונקציות שיפוט ואסטרטגיה ==============

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
            model="claude-sonnet-4-6",
            max_tokens=800,
            system=JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": judge_prompt}],
        )
        txt = "".join([getattr(block, 'text', '') for block in (res.content or []) if getattr(block, 'type', None) == 'text'])
        m = re.search(r'\{[\s\S]*\}', txt)
        if m: return _json.loads(m.group(0))
    except Exception as e:
        return {"error": str(e)[:150]}
    return None

def generate_content_brief(claude_client, question, gap, judgments, sources):
    """מייצר Content Brief מעשי מבוסס על הפער שזוהה והמקורות."""
    if not claude_client: return None
    judge_verdicts = [f"[{m}] ציון {j.get('score','?')}/10 · {j.get('verdict','')}" 
                      for m, j in (judgments or {}).items() if j and not j.get('error')]
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
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=CONTENT_BRIEF_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        txt = "".join([getattr(block, 'text', '') for block in (res.content or []) if getattr(block, 'type', None) == 'text'])
        m = re.search(r'\{[\s\S]*\}', txt)
        if m: return _json.loads(m.group(0))
    except Exception as e:
        return {"error": str(e)[:150]}
    return None

# ============== הפונקציה הראשית: הרצת הסריקה ==============

def run_chat_audit(chat_ph):
    """Animated chat-style audit. Renders all bubbles progressively into chat_ph."""
    if not g_key:
        st.error("חסר מפתח Google (GOOGLE_API_KEY) ב-.env")
        return
    
    if not a_key or not a_key.strip():
        st.warning("⚠️ מפתח Claude (ANTHROPIC_API_KEY) לא מוגדר ב-.env. כמה תכונות לא יהיו זמינות.")
    
    google_client = genai.Client(api_key=g_key.strip())
    openai_client = OpenAI(api_key=o_key.strip(), http_client=httpx.Client(verify=False)) if o_key.strip() else None
    claude_client = None
    if _ANTHROPIC_AVAILABLE and a_key and a_key.strip():
        try:
            claude_client = Anthropic(api_key=a_key.strip(), http_client=httpx.Client(verify=False))
        except TypeError:
            claude_client = Anthropic(api_key=a_key.strip())
        except Exception as e:
            st.warning(f"⚠️ שגיאה בחיבור ל-Claude API: {str(e)[:150]}")

    try:
        gemini_config = genai_types.GenerateContentConfig(
            system_instruction=BRAND_AUDIT_SYSTEM_PROMPT,
            tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())],
            thinking_config=genai_types.ThinkingConfig(include_thoughts=True),
        )
    except Exception:
        gemini_config = genai_types.GenerateContentConfig(
            tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())]
        )

    st.session_state.audit_results = []
    bubbles_html = ""
    header_html = '<div class="chat-header"><div class="chat-avatar">AI</div><div class="chat-head-txt"><div class="chat-head-name">GEO Radar · סורק נוכחות AI</div><div class="chat-head-status">פעיל</div></div></div>'

    def render(extra_inside=""):
        chat_ph.markdown(f'<div class="chat-wrap">{header_html}{bubbles_html}{extra_inside}</div>', unsafe_allow_html=True)

    for idx, q in enumerate(FIXED_QUESTIONS):
        bubbles_html += _bubble_user(q)
        render(_bubble_ai_typing())
        time.sleep(0.4)

        # --- Gemini ---
        ans_g, gemini_sources, gemini_thinking = "", [], ""
        gemini_models = ['gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-2.0-flash']
        success = False
        for model_name in gemini_models:
            for attempt in range(2):
                try:
                    res_g = google_client.models.generate_content(model=model_name, contents=q, config=gemini_config)
                    gemini_thinking = extract_gemini_thinking(res_g)
                    full_text = res_g.text or ""
                    ans_g = full_text.replace(gemini_thinking, "").strip() if gemini_thinking in full_text else full_text
                    gemini_sources = extract_gemini_citations(res_g)
                    success = True
                    break
                except Exception as eg:
                    msg = str(eg)
                    if attempt == 0 and any(s in msg for s in ['429', 'RESOURCE_EXHAUSTED', 'quota']):
                        time.sleep(9); continue
                    if attempt == 0 and any(s in msg for s in ['503', 'UNAVAILABLE', 'overload', 'timeout']):
                        time.sleep(3); continue
                    break
            if success: break
        if not ans_g: ans_g = "⚠️ שגיאת Gemini"

        # --- ChatGPT ---
        ans_o, openai_sources, openai_thinking, openai_search_queries = "לא בוצע", [], "", []
        if openai_client:
            try:
                res_o = openai_client.responses.create(model="o4-mini", instructions=BRAND_AUDIT_SYSTEM_PROMPT, input=q, tools=[{"type": "web_search"}], reasoning={"summary": "auto"})
                ans_o, openai_sources, openai_thinking, openai_search_queries = extract_openai_responses(res_o)
            except Exception:
                try:
                    res_o = openai_client.chat.completions.create(model="gpt-4o-search-preview", web_search_options={}, messages=[{"role": "system", "content": BRAND_AUDIT_SYSTEM_PROMPT}, {"role": "user", "content": q}])
                    ans_o = res_o.choices[0].message.content or ""
                    openai_sources = extract_openai_citations(res_o)
                except Exception as eo: ans_o = f"⚠️ שגיאת OpenAI: {str(eo)[:100]}"

        # --- Claude ---
        ans_c, claude_sources, claude_thinking, claude_search_queries = "לא בוצע", [], "", []
        if claude_client:
            try:
                res_c = claude_client.messages.create(model="claude-sonnet-4-6", max_tokens=2048, system=BRAND_AUDIT_SYSTEM_PROMPT, tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}], messages=[{"role": "user", "content": q}])
                ans_c, claude_sources, claude_thinking, claude_search_queries = extract_claude_response(res_c)
            except Exception as ec:
                try:
                    res_c = claude_client.messages.create(model="claude-opus-4-7", max_tokens=2048, system=BRAND_AUDIT_SYSTEM_PROMPT, tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}], messages=[{"role": "user", "content": q}])
                    ans_c, claude_sources, claude_thinking, claude_search_queries = extract_claude_response(res_c)
                except Exception: ans_c = f"⚠️ שגיאת Claude"

        sources = merge_sources(gemini_sources, openai_sources, claude_sources)

        # --- Judgments & Brief ---
        judgments = {"openai": None, "gemini": None, "claude": None}
        if claude_client:
            judgments["openai"] = judge_answer(claude_client, q, ans_o, openai_sources, "ChatGPT")
            judgments["gemini"] = judge_answer(claude_client, q, ans_g, gemini_sources, "Gemini")
            judgments["claude"] = judge_answer(claude_client, q, ans_c, claude_sources, "Claude")

        quick_gap = {
            "company_in_openai": bool(detect_mentions(ans_o, [DEFAULT_COMPANY], COMPANY_ALIASES)),
            "company_in_gemini": bool(detect_mentions(ans_g, [DEFAULT_COMPANY], COMPANY_ALIASES)),
            "company_in_claude": bool(detect_mentions(ans_c, [DEFAULT_COMPANY], COMPANY_ALIASES)),
            "company_in_sources": any(any(al.lower() in (s.get('title','')+s.get('content','')+s.get('url','')).lower() for al in [DEFAULT_COMPANY]+COMPANY_ALIASES.get(DEFAULT_COMPANY, [])) for s in sources),
        }
        quick_gap["score"] = sum(25 for k in ["company_in_openai","company_in_gemini","company_in_claude","company_in_sources"] if quick_gap[k])
        
        content_brief = generate_content_brief(claude_client, q, quick_gap, judgments, sources) if claude_client and quick_gap["score"] < 75 else None

        st.session_state.audit_results.append({
            "question": q, "gemini": ans_g, "openai": ans_o, "claude": ans_c,
            "gemini_sources": gemini_sources, "openai_sources": openai_sources, "claude_sources": claude_sources,
            "gemini_thinking": gemini_thinking, "openai_thinking": openai_thinking, "claude_thinking": claude_thinking,
            "openai_search_queries": openai_search_queries, "claude_search_queries": claude_search_queries,
            "sources": sources, "judgments": judgments, "content_brief": content_brief,
        })
        
        bubbles_html += _bubble_ai_done(len(sources), [domain_of(s['url']) for s in sources])
        render()
        if idx < len(FIXED_QUESTIONS) - 1: time.sleep(3)

    bubbles_html += '<div class="bubble-row bubble-row-ai"><div class="bubble-ai">🎉 הסריקה הושלמה! מעבר לדשבורד...</div></div>'
    render()
    time.sleep(1.2)