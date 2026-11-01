# app.py
# ─────────────────────────────────────────────
# theAIgency: an AI job market. Businesses post roles, AI workers apply,
# owners earn. Same look as the AI Agent Market library.
# ─────────────────────────────────────────────
from __future__ import annotations

import base64
import html

import streamlit as st

import interview
import llm
import store
from theme_manager import get_palette, init_theme, render_theme_toggle

st.set_page_config(page_title="theAIgency · AI Job Market", layout="wide", initial_sidebar_state="collapsed")
init_theme()
pal = get_palette()
e = html.escape

db = store.load()
qp = st.query_params
page = qp.get("page", "home")


# ────────────────────────────────
# Icons and logos (same gradient-tile style as the library)
# ────────────────────────────────
def _svg_data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


def icon_tile(path: str, c1: str, c2: str, size: int, gid: str = "gt") -> str:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">'
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
        f'<rect width="48" height="48" rx="11" fill="url(#{gid})"/>'
        f'<g transform="translate(12 12)" fill="none" stroke="#ffffff" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{path}</g></svg>'
    )
    return f'<img src="{_svg_data_uri(svg)}" width="{size}" height="{size}" alt="" style="display:block;border-radius:{size // 4}px;"/>'


CATEGORY_ICONS = {
    "Banking & Finance": '<path d="M12 3l9 5H3z"/><path d="M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 21h18"/>',
    "Legal & Compliance": '<path d="M12 3v18M7 21h10M5 7h14"/><path d="M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>',
    "IT & DevOps": '<rect x="3" y="4" width="18" height="7" rx="1.5"/><rect x="3" y="13" width="18" height="7" rx="1.5"/><path d="M7 7.5h.01M7 16.5h.01"/>',
    "Software Engineering": '<path d="M8 6l-6 6 6 6M16 6l6 6-6 6M14 4l-4 16"/>',
    "Data & Analytics": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "Customer Support": '<path d="M4 13v-1a8 8 0 0 1 16 0v1"/><rect x="2" y="13" width="5" height="6" rx="1.5"/><rect x="17" y="13" width="5" height="6" rx="1.5"/>',
    "Marketing & Content": '<path d="M3 11v2l13 5V6z"/><path d="M16 9a3 3 0 0 1 0 6M7 14l1 6h3l-1-5"/>',
    "Real Estate": '<path d="M3 11l9-7 9 7v10H3z"/><path d="M9 21v-6h6v6"/>',
    "Executive": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/>',
}
CATEGORY_GRADIENTS = {
    "Banking & Finance": ("#1739c9", "#4f7bff"),
    "Legal & Compliance": ("#312e81", "#6d7cff"),
    "IT & DevOps": ("#0369a1", "#22d3ee"),
    "Software Engineering": ("#1a6dff", "#00c6ff"),
    "Data & Analytics": ("#0e7490", "#2dd4bf"),
    "Customer Support": ("#1e3a8a", "#60a5fa"),
    "Marketing & Content": ("#9f1239", "#ff5a76"),
    "Real Estate": ("#0c4a6e", "#38bdf8"),
    "Executive": ("#0b2a6b", "#1a6dff"),
}
_DEFAULT_ICON = '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>'
ICON_AGENT = '<rect x="4" y="7" width="16" height="12" rx="3"/><path d="M12 3v4M9 12h.01M15 12h.01M9 16h6M2 12v3M22 12v3"/>'
ICON_POST = '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M12 11v5M9.5 13.5h5"/>'
ICON_WALLET = '<rect x="3" y="6" width="18" height="14" rx="2"/><path d="M3 10h18M16 15h2"/>'
ICON_SEARCH = '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.5-4.5"/>'


def category_logo(category: str, size: int = 52, agent: bool = False) -> str:
    c1, c2 = CATEGORY_GRADIENTS.get(category, ("#1a6dff", "#00c6ff"))
    path = ICON_AGENT if agent else CATEGORY_ICONS.get(category, _DEFAULT_ICON)
    gid = ("a" if agent else "c") + "".join(ch for ch in category if ch.isalnum())
    return icon_tile(path, c1, c2, size, gid=gid)


BRAND_LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">'
    '<defs><linearGradient id="aig" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#e5133a"/><stop offset="0.55" stop-color="#7a3cff"/><stop offset="1" stop-color="#1a6dff"/></linearGradient></defs>'
    '<rect width="40" height="40" rx="10" fill="url(#aig)"/>'
    # a briefcase with an agent "eye" pair: AI workers for hire
    '<rect x="8" y="14" width="24" height="16" rx="3" fill="#ffffff"/>'
    '<path d="M15 14v-3a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v3" fill="none" stroke="#ffffff" stroke-width="2.2"/>'
    '<circle cx="16" cy="22" r="2" fill="#7a3cff"/><circle cx="24" cy="22" r="2" fill="#1a6dff"/>'
    '</svg>'
)


# ────────────────────────────────
# CSS: library marketplace styles + job market additions
# ────────────────────────────────
def render_css():
    accent = pal["accent"]
    st.markdown(
        f"""
<style>
.block-container, [data-testid="stMainBlockContainer"] {{ max-width: 1320px !important; padding-top: 0 !important; }}
[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stMain"] {{ overflow-x: hidden; }}
[data-testid="stElementContainer"]:has(style) {{ display: none !important; }}
.st-key-aw_header, .st-key-aw_hero {{ width: 100vw !important; max-width: 100vw !important; margin-left: calc(50% - 50vw) !important; }}
.st-key-aw_header {{
    background: #0a1428; padding: 1rem max(2rem, calc(50vw - 640px)) 0 max(2rem, calc(50vw - 640px)); gap: 0 !important;
    box-shadow: 0 10px 30px -18px rgba(10,20,40,0.9);
}}
.st-key-aw_header p, .st-key-aw_header span, .st-key-aw_header label {{ color:#e6edf7 !important; }}
.aw-brand {{ display:flex; align-items:center; gap:0.8rem; text-decoration:none !important; }}
.aw-word {{ font-size:1.75rem; font-weight:800; color:#ffffff !important; letter-spacing:-0.025em; line-height:1; }}
.aw-word b {{ color:{pal['red']} !important; font-weight:800; text-shadow:0 0 16px rgba(229,19,58,0.55); }}
.aw-word small {{ display:block; font-size:0.7rem; font-weight:600; color:#8fb3d9 !important; letter-spacing:0.12em; text-transform:uppercase; margin-top:6px; }}
.aw-head-actions {{ display:flex; justify-content:flex-end; gap:0.75rem; align-items:center; }}
.aw-head-actions a {{ font-size:0.9rem; font-weight:600; text-decoration:none !important; white-space:nowrap; }}
.aw-btn-red {{ background:{pal['red']}; color:#ffffff !important; padding:0.6rem 1.15rem; border-radius:8px; box-shadow:0 0 18px rgba(229,19,58,0.45); }}
.aw-btn-red:hover {{ filter:brightness(1.1); }}
.aw-btn-ghost {{ color:#e6edf7 !important; padding:0.55rem 1rem; border-radius:8px; border:1px solid rgba(255,255,255,0.28); }}
.aw-btn-ghost:hover {{ border-color:#3ea6ff; color:#3ea6ff !important; }}
.aw-nav {{
    display:flex; gap:1.9rem; flex-wrap:wrap; align-items:center;
    margin: 0.9rem calc(-1 * max(2rem, calc(50vw - 640px))) 0; padding: 0.7rem max(2rem, calc(50vw - 640px));
    background:#13213d; border-bottom: 4px solid transparent;
    border-image: linear-gradient(90deg, {pal['red']} 0%, {pal['red']} 35%, {accent} 65%, {accent} 100%) 1;
}}
.aw-nav a {{ color:#e6edf7 !important; font-size:0.95rem; font-weight:600; text-decoration:none !important; }}
.aw-nav a:hover {{ color:#3ea6ff !important; }}
.aw-nav .aw-nav-right {{ margin-left:auto; display:flex; gap:1.9rem; }}
/* Hero */
.st-key-aw_hero {{
    background:
        radial-gradient(700px 260px at 12% 0%, rgba(229,19,58,0.10), transparent 60%),
        radial-gradient(800px 300px at 88% 10%, rgba(26,109,255,0.16), transparent 60%),
        {pal['hero_bg']};
    padding: 3rem max(2rem, calc(50vw - 540px)) 2.5rem; margin-bottom: 1.5rem;
}}
.aw-eyebrow {{ text-align:center; font-weight:700; font-size:0.95rem; color:{pal['hero_text']} !important; letter-spacing:0.02em; }}
.aw-eyebrow i {{ color:{pal['red']}; font-style:normal; text-shadow:0 0 10px rgba(229,19,58,0.5); }}
.aw-hero-title, .aw-hero-title * {{ text-align:center; font-size:2.6rem !important; font-weight:800 !important; letter-spacing:-0.03em !important; color:{pal['hero_text']} !important; margin:0.4rem 0 0.4rem 0 !important; line-height:1.15 !important; }}
.aw-hero-title em {{ font-style:normal; color:{pal['red']} !important; }}
.aw-hero-sub {{ text-align:center; font-size:1.08rem; color:{pal['subtext']} !important; margin-bottom:1.5rem; }}
.st-key-aw_hero [data-baseweb="input"] {{ border-radius: 10px !important; border: 1px solid {pal['hero_border']} !important; background:{pal['hero_card']} !important; overflow:hidden; }}
.st-key-aw_hero [data-baseweb="input"]:focus-within {{ border-color:{accent} !important; box-shadow:0 0 0 3px rgba(26,109,255,0.18), 0 0 22px rgba(0,170,255,0.35); }}
.st-key-aw_hero [data-baseweb="input"] input {{ height: 54px; font-size: 1rem !important; color:{pal['hero_text']} !important; background:{pal['hero_card']} !important; border:none !important; padding-left:1rem !important; }}
.aw-disclaimer {{ font-size:0.76rem; color:{pal['muted']} !important; margin-top:0.3rem; }}
.aw-h3 {{ font-size:1.15rem; font-weight:700; color:{pal['hero_text']} !important; margin:1.4rem 0 0.7rem 0; }}
.aw-tasks {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }}
.aw-task {{ display:flex; gap:0.9rem; align-items:flex-start; background:{pal['hero_card']}; border:1px solid {pal['hero_border']}; border-radius:12px; padding:1rem 1.1rem; text-decoration:none !important; transition: border-color .15s, box-shadow .15s; }}
.aw-task:hover {{ border-color:{accent}; box-shadow:0 0 0 1px {accent}, 0 8px 24px -12px rgba(26,109,255,0.55); }}
.aw-task-icon {{ flex:none; border-radius:8px; box-shadow:0 0 12px rgba(0,170,255,0.5); }}
.aw-task b {{ display:block; color:{pal['hero_text']} !important; font-size:0.95rem; }}
.aw-task span {{ color:{pal['subtext']} !important; font-size:0.86rem; }}
/* Stat strip */
.mk-stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:0.5rem; }}
.mk-stat {{ background:{pal['card']}; border:1px solid {pal['border']}; border-top:3px solid {accent}; border-radius:12px; padding:0.9rem 1.1rem; }}
.mk-stat:nth-child(odd) {{ border-top-color:{pal['red']}; }}
.mk-stat b {{ display:block; font-size:1.6rem; font-weight:800; color:{pal['text']} !important; letter-spacing:-0.02em; }}
.mk-stat span {{ font-size:0.74rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:{pal['muted']} !important; }}
/* Section headings */
.aw-h2 {{ text-align:center; font-size:1.45rem; font-weight:700; color:{pal['text']} !important; margin:1.8rem 0 0.6rem 0; }}
.aw-h2-left {{ font-size:1.2rem; font-weight:700; color:{pal['text']} !important; margin:1.4rem 0 0.6rem 0; }}
/* Cards */
.aw-cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:18px; margin-top:0.8rem; }}
.aw-card {{ background:{pal['card']}; border:1px solid {pal['border']}; border-radius:14px; padding:1.1rem 1.2rem; display:flex; flex-direction:column; gap:0.5rem; min-height:300px; transition: box-shadow .15s, border-color .15s; }}
.aw-card:hover {{ border-color:{accent}; box-shadow:0 10px 30px -14px rgba(26,109,255,0.55); }}
.aw-card-top {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.3rem; }}
.aw-logo {{ padding:4px; border:1px solid {pal['border']}; border-radius:12px; background:{pal['card']}; flex:none; }}
.aw-rank {{ background:{pal['red']}; color:#ffffff !important; font-size:0.75rem; font-weight:700; padding:2px 9px; border-radius:6px; box-shadow:0 0 12px rgba(229,19,58,0.45); }}
.aw-by {{ font-size:0.8rem; color:{pal['muted']} !important; }}
.aw-by b {{ color:{pal['subtext']} !important; font-weight:600; }}
.aw-title {{ font-size:1.02rem; font-weight:700; color:{accent} !important; line-height:1.3; text-decoration:none !important; }}
a.aw-title:hover {{ text-decoration:underline !important; }}
.aw-rating {{ display:flex; align-items:center; gap:6px; font-size:0.85rem; }}
.aw-rating b {{ color:{pal['text']} !important; }}
.aw-stars {{ color:{accent} !important; letter-spacing:1px; font-size:1rem; text-shadow:0 0 8px rgba(26,109,255,0.35); }}
.aw-stars-off {{ color:{pal['border']} !important; text-shadow:none; }}
.aw-rating-n {{ color:{accent} !important; font-size:0.8rem; }}
.aw-rating-none {{ color:{pal['muted']} !important; font-size:0.8rem; }}
.aw-tags {{ display:flex; gap:6px; flex-wrap:wrap; }}
.aw-tag {{ font-size:0.74rem; padding:2px 9px; border-radius:6px; border:1px solid {pal['input_border']}; color:{pal['subtext']} !important; }}
.aw-tag-free {{ border-color:{accent}; color:{accent} !important; font-weight:600; }}
.aw-desc {{ font-size:0.86rem; line-height:1.5; color:{pal['subtext']} !important; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
.aw-card .aw-desc {{ flex:1; }}
.aw-card-actions {{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; }}
.aw-card .aw-card-actions {{ padding-top:0.7rem; border-top:1px solid {pal['border']}; justify-content:space-between; }}
.aw-price {{ font-size:0.95rem; font-weight:700; color:{pal['text']} !important; }}
.aw-price small {{ font-weight:500; color:{pal['muted']} !important; font-size:0.78rem; }}
/* Groups + rows */
.aw-vgroup {{ margin-top:0.9rem; }}
.aw-vgroup > summary {{ list-style:none; cursor:pointer; display:flex; align-items:center; gap:0.75rem; padding:0.75rem 1.1rem; background:{pal['card']}; border:1px solid {pal['border']}; border-radius:12px; transition:border-color .15s; }}
.aw-vgroup > summary::-webkit-details-marker {{ display:none; }}
.aw-vgroup > summary:hover {{ border-color:{accent}; }}
.aw-vgroup > summary h3 {{ margin:0 !important; font-size:1.08rem !important; }}
.aw-vgroup > summary .aw-vcount {{ color:{pal['muted']} !important; font-size:0.84rem; margin-left:auto; }}
.aw-vgroup > summary::after {{ content:"▾"; color:{pal['muted']}; font-size:1rem; transition:transform .15s; }}
.aw-vgroup[open] > summary {{ border-radius:12px 12px 0 0; box-shadow:inset 0 -2px 0 {accent}; }}
.aw-vgroup[open] > summary::after {{ transform:rotate(180deg); color:{accent}; }}
.aw-list {{ background:{pal['card']}; border:1px solid {pal['border']}; border-top:none; border-radius:0 0 12px 12px; }}
.aw-list-solo {{ border-top:1px solid {pal['border']}; border-radius:12px; }}
.aw-row {{ display:flex; gap:1rem; align-items:flex-start; padding:1rem 1.2rem; border-bottom:1px solid {pal['border']}; }}
.aw-row:last-child {{ border-bottom:none; border-radius:0 0 12px 12px; }}
.aw-row:hover {{ background:{pal['table_hover_bg']}; }}
.aw-row-main {{ flex:1; display:flex; flex-direction:column; gap:0.3rem; min-width:0; }}
.aw-desc-row {{ -webkit-line-clamp:2; }}
.aw-row-side {{ display:flex; flex-direction:column; align-items:flex-end; gap:0.5rem; flex:none; min-width:170px; }}
.aw-badge {{ font-size:0.72rem; font-weight:600; padding:2px 9px; border-radius:999px; white-space:nowrap; }}
.aw-badge-new {{ background:rgba(0,190,255,0.12); color:#0891d1 !important; border:1px solid rgba(0,190,255,0.4); }}
.aw-badge-live {{ background:rgba(26,109,255,0.10); color:{accent} !important; border:1px solid rgba(26,109,255,0.35); }}
.aw-badge-soft {{ background:{pal['bg']}; color:{pal['subtext']} !important; border:1px solid {pal['border']}; }}
.aw-badge-muted {{ color:{pal['muted']} !important; border:1px dashed {pal['input_border']}; }}
.aw-cta {{ font-size:0.84rem; font-weight:600; padding:6px 14px; border-radius:8px; white-space:nowrap; background:{pal['red']}; color:#ffffff !important; text-decoration:none !important; box-shadow:0 0 14px rgba(229,19,58,0.35); }}
.aw-cta:hover {{ filter:brightness(1.08); }}
.aw-cta-blue {{ background:transparent; border:1px solid {accent}; color:{accent} !important; box-shadow:none; }}
.aw-cta-blue:hover {{ background:rgba(26,109,255,0.08); }}
.aw-cta-off {{ background:transparent; color:{pal['muted']} !important; border:1px solid {pal['border']}; box-shadow:none; }}
.st-key-aw_filters_jobs, .st-key-aw_filters_workers {{ position: sticky; top: 1rem; }}
/* Token bandwidth meter */
.bw {{ display:flex; flex-direction:column; gap:4px; width:100%; }}
.bw-head {{ display:flex; justify-content:space-between; align-items:center; gap:8px; font-size:0.76rem; }}
.bw-head span {{ color:{pal['muted']} !important; white-space:nowrap; }}
.bw-pill {{ font-size:0.72rem; font-weight:700; padding:1px 8px; border-radius:999px; white-space:nowrap; }}
.bw-ok .bw-pill {{ background:rgba(16,185,129,0.12); color:#059669 !important; border:1px solid rgba(16,185,129,0.4); }}
.bw-low .bw-pill {{ background:rgba(245,158,11,0.12); color:#b45309 !important; border:1px solid rgba(245,158,11,0.45); }}
.bw-off .bw-pill {{ background:rgba(229,19,58,0.08); color:{pal['red']} !important; border:1px solid rgba(229,19,58,0.4); }}
.bw-bar {{ height:6px; border-radius:999px; background:{pal['border']}; overflow:hidden; }}
.bw-bar i {{ display:block; height:100%; border-radius:999px; background:linear-gradient(90deg,{accent},#00c6ff); }}
.bw-low .bw-bar i {{ background:linear-gradient(90deg,#f59e0b,#fbbf24); }}
.bw-off .bw-bar i {{ background:linear-gradient(90deg,{pal['red']},#ff5a76); }}
/* Detail pages */
.ad-crumbs {{ font-size:0.88rem; margin:1.1rem 0 1rem 0; color:{pal['muted']} !important; }}
.ad-head {{ display:flex; gap:1.2rem; align-items:flex-start; background:{pal['card']}; border:1px solid {pal['border']}; border-radius:14px; padding:1.3rem 1.4rem; }}
.ad-head-main {{ flex:1; display:flex; flex-direction:column; gap:0.4rem; min-width:0; }}
.ad-head h1 {{ margin:0 !important; font-size:1.7rem !important; font-weight:800 !important; }}
.ad-head-side {{ width:280px; flex:none; display:flex; flex-direction:column; gap:0.7rem; }}
.ad-box {{ background:{pal['card']}; border:1px solid {pal['border']}; border-radius:12px; padding:1rem 1.2rem; margin-top:1rem; }}
.ad-box h4 {{ margin:0 0 0.6rem 0 !important; font-size:1.02rem !important; }}
.ad-box p {{ font-size:0.92rem; line-height:1.6; margin:0; }}
.ad-kv {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }}
.ad-kv div {{ background:{pal['bg']}; border:1px solid {pal['border']}; border-radius:10px; padding:0.6rem 0.8rem; }}
.ad-kv span {{ display:block; font-size:0.7rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:{pal['muted']} !important; }}
.ad-kv b {{ font-size:1.05rem; color:{pal['text']} !important; }}
/* Resume timeline */
.rs-item {{ position:relative; padding:0.2rem 0 1.1rem 1.4rem; border-left:2px solid {pal['border']}; margin-left:0.4rem; }}
.rs-item:last-child {{ padding-bottom:0.2rem; }}
.rs-item::before {{ content:""; position:absolute; left:-7px; top:0.35rem; width:12px; height:12px; border-radius:50%; background:linear-gradient(135deg,{pal['red']},{accent}); box-shadow:0 0 10px rgba(26,109,255,0.4); }}
.rs-top {{ display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap; }}
.rs-top b {{ color:{pal['text']} !important; font-size:0.98rem; }}
.rs-meta {{ font-size:0.8rem; color:{pal['muted']} !important; }}
.aw-quote {{ background:{pal['bg']}; border:1px solid {pal['border']}; border-left:3px solid {accent}; border-radius:8px; padding:0.6rem 0.85rem; margin-top:0.45rem; font-size:0.88rem; }}
footer.mk-foot {{ font-size:0.8rem; color:{pal['muted']} !important; text-align:center; margin:2.5rem 0 1rem; }}
@media (max-width: 1100px) {{ .aw-cards, .aw-tasks, .mk-stats {{ grid-template-columns:repeat(2,1fr); }} .ad-kv {{ grid-template-columns:repeat(2,1fr); }} }}
@media (max-width: 700px) {{ .aw-cards, .aw-tasks, .mk-stats {{ grid-template-columns:1fr; }} .aw-row, .ad-head {{ flex-wrap:wrap; }} .aw-row-side {{ align-items:flex-start; }} .ad-head-side {{ width:100%; }} }}
</style>
""",
        unsafe_allow_html=True,
    )


# ────────────────────────────────
# HTML snippets
# ────────────────────────────────
def stars_html(agent: dict) -> str:
    avg, n = store.rating(agent)
    if not n:
        return "<span class='aw-rating'><span class='aw-rating-none'>No reviews yet</span></span>"
    full = int(round(avg))
    return (
        f"<span class='aw-rating'><b>{avg:.1f}</b>"
        f"<span class='aw-stars'>{'★' * full}<span class='aw-stars-off'>{'★' * (5 - full)}</span></span>"
        f"<span class='aw-rating-n'>({n} review{'s' if n != 1 else ''})</span></span>"
    )


def bandwidth_html(agent: dict) -> str:
    label, cls = store.availability(db, agent)
    used = store.tokens_used(db, agent["id"])
    cap = agent["token_capacity"]
    pct = min(100, round(100 * used / cap)) if cap else 100
    return (
        f"<div class='bw {cls}'>"
        f"<div class='bw-head'><span class='bw-pill'>{e(label)}</span>"
        f"<span>{store.tokens_free(db, agent)}M / {cap}M tokens free</span></div>"
        f"<div class='bw-bar'><i style='width:{pct}%'></i></div></div>"
    )


def skills_html(skills: list[str], highlight: set[str] | None = None) -> str:
    hl = highlight or set()
    return "<div class='aw-tags'>" + "".join(
        f"<span class='aw-tag{' aw-tag-free' if s.lower() in hl else ''}'>{e(s)}</span>" for s in skills
    ) + "</div>"


def budget_html(job: dict) -> str:
    unit = "/ month" if job["budget_type"] == "per month" else "fixed"
    return f"<span class='aw-price'>${job['budget']:,} <small>{unit}</small></span>"


def agent_card_html(agent: dict, rank: int) -> str:
    return (
        "<div class='aw-card'>"
        "<div class='aw-card-top'>"
        f"<div class='aw-logo'>{category_logo(agent['category'], 46, agent=True)}</div>"
        f"<span class='aw-rank'>Top {rank}</span></div>"
        f"<div class='aw-by'>Owner: <b>{e(agent['owner'])}</b> · {e(agent['category'])}</div>"
        f"<a class='aw-title' href='?page=worker&id={e(agent['id'])}' target='_self'>{e(agent['name'])}</a>"
        f"{stars_html(agent)}"
        f"<div class='aw-desc'>{e(agent['tagline'])}</div>"
        f"{bandwidth_html(agent)}"
        "<div class='aw-card-actions'>"
        f"<span class='aw-price'>${agent['rate']:,} <small>/ month</small></span>"
        f"<a class='aw-cta' href='?page=worker&id={e(agent['id'])}' target='_self'>View resume</a>"
        "</div></div>"
    )


def agent_row_html(agent: dict) -> str:
    done = len(agent["missions"])
    return (
        "<div class='aw-row'>"
        f"<div class='aw-logo'>{category_logo(agent['category'], 52, agent=True)}</div>"
        "<div class='aw-row-main'>"
        f"<a class='aw-title' href='?page=worker&id={e(agent['id'])}' target='_self'>{e(agent['name'])}</a>"
        f"<div class='aw-by'>Created by <b>{e(agent['creator'])}</b> · Owned by <b>{e(agent['owner'])}</b> · {e(agent['model'])}</div>"
        f"<div class='aw-desc aw-desc-row'>{e(agent['tagline'])}</div>"
        f"{skills_html(agent['skills'])}"
        "</div>"
        "<div class='aw-row-side'>"
        f"{stars_html(agent)}"
        f"<span class='aw-badge aw-badge-soft'>{done} mission{'s' if done != 1 else ''} done</span>"
        f"{bandwidth_html(agent)}"
        f"<span class='aw-price'>${agent['rate']:,} <small>/ month</small></span>"
        "</div></div>"
    )


JOB_STATUS = {
    "open": ("Hiring", "aw-badge-new"),
    "in_progress": ("Mission in progress", "aw-badge-live"),
    "completed": ("Completed", "aw-badge-muted"),
}


def job_row_html(job: dict) -> str:
    label, cls = JOB_STATUS[job["status"]]
    n = len(job["applications"])
    cta = (f"<a class='aw-cta' href='?page=job&id={e(job['id'])}' target='_self'>Apply as AI agent</a>"
           if job["status"] == "open" else
           f"<a class='aw-cta aw-cta-blue' href='?page=job&id={e(job['id'])}' target='_self'>View</a>")
    return (
        "<div class='aw-row'>"
        f"<div class='aw-logo'>{category_logo(job['category'], 52)}</div>"
        "<div class='aw-row-main'>"
        f"<a class='aw-title' href='?page=job&id={e(job['id'])}' target='_self'>{e(job['title'])}</a>"
        f"<div class='aw-by'><b>{e(job['company'])}</b> · Posted {e(job['posted'])} · {e(job['category'])}</div>"
        f"<div class='aw-desc aw-desc-row'>{e(job['description'])}</div>"
        f"{skills_html(job['skills'])}"
        "</div>"
        "<div class='aw-row-side'>"
        f"<span class='aw-badge {cls}'>{label}</span>"
        f"{budget_html(job)}"
        f"<span class='aw-by'>Needs {job['tokens_month']}M tokens / month · {n} applicant{'s' if n != 1 else ''}</span>"
        f"<div class='aw-card-actions'>{cta}</div>"
        "</div></div>"
    )


def group_html(title: str, category: str, rows: list[str], count_label: str, is_open: bool, agent: bool = False) -> str:
    return (
        f"<details class='aw-vgroup'{' open' if is_open else ''}><summary>"
        f"{category_logo(category, 32, agent=agent)}<h3>{e(title)}</h3>"
        f"<span class='aw-vcount'>{count_label}</span></summary>"
        f"<div class='aw-list'>{''.join(rows)}</div></details>"
    )


# ────────────────────────────────
# Header (shared by every page)
# ────────────────────────────────
def render_header():
    with st.container(key="aw_header"):
        brand, actions, tog = st.columns([5, 3.4, 0.8], vertical_alignment="center")
        with brand:
            st.markdown(
                f"<a class='aw-brand' href='?' target='_self'><img src='{_svg_data_uri(BRAND_LOGO_SVG)}' width='52' height='52' alt=''/>"
                "<span class='aw-word'>the <b>AIgency</b><small>The job market for AI workers</small></span></a>",
                unsafe_allow_html=True,
            )
        with actions:
            st.markdown(
                "<div class='aw-head-actions'>"
                "<a class='aw-btn-ghost' href='?page=register' target='_self'>List your AI agent</a>"
                "<a class='aw-btn-red' href='?page=post' target='_self'>Post a job</a>"
                "</div>",
                unsafe_allow_html=True,
            )
        with tog:
            render_theme_toggle(label="Dark", key="aw_theme_toggle")
        st.markdown(
            "<nav class='aw-nav'>"
            "<a href='?#open-jobs' target='_self'>Find jobs</a>"
            "<a href='?#ai-workers' target='_self'>Find AI workers</a>"
            "<a href='?page=post' target='_self'>Post a job</a>"
            "<a href='?page=register' target='_self'>List your agent</a>"
            "<a href='?page=owner' target='_self'>Owner earnings</a>"
            "<span class='aw-nav-right'><a href='http://100.31.100.157:8502/' target='_blank'>AI Agent Library</a></span>"
            "</nav>",
            unsafe_allow_html=True,
        )


def footer():
    st.markdown(
        "<footer class='mk-foot'>theAIgency · AI job market · Open AIgents Sandbox Initiative · "
        "Demo data, no real payments.</footer>",
        unsafe_allow_html=True,
    )


def matches(q: str, *fields) -> bool:
    if not q:
        return True
    hay = " ".join(str(f) for f in fields).lower()
    return all(term in hay for term in q.split())


# ────────────────────────────────
# PAGE: home
# ────────────────────────────────
def page_home():
    agents, jobs = db["agents"], db["jobs"]
    open_jobs = [j for j in jobs if j["status"] == "open"]

    with st.container(key="aw_hero"):
        st.markdown(
            "<div class='aw-eyebrow'><i>✦</i> AI job market</div>"
            f"<h1 class='aw-hero-title'>Hire from <em>{len(agents)} proven</em> AI workers, or put your agent to work</h1>"
            "<div class='aw-hero-sub'>Every AI worker has a resume of past missions and employer reviews. "
            "Owners earn on their agent's behalf.</div>",
            unsafe_allow_html=True,
        )
        query = st.text_input(
            "Search",
            placeholder="Search jobs and AI workers, e.g. \"kyc\", \"kubernetes\", \"contract review\"…",
            key="mk_search",
            label_visibility="collapsed",
        )
        st.markdown(
            "<div class='aw-disclaimer'>AI workers only apply when they have the token bandwidth to deliver. Demo data, no real payments.</div>"
            "<div class='aw-h3'>Get started</div>"
            "<div class='aw-tasks'>"
            f"<a class='aw-task' href='?page=post' target='_self'><div class='aw-task-icon'>{icon_tile(ICON_POST, '#e5133a', '#ff5a76', 32, gid='t1')}</div>"
            "<div><b>Post a job</b><span>Describe the role your business needs filled.</span></div></a>"
            f"<a class='aw-task' href='#ai-workers' target='_self'><div class='aw-task-icon'>{icon_tile(ICON_SEARCH, '#1a6dff', '#00c6ff', 32, gid='t2')}</div>"
            "<div><b>Find AI workers</b><span>Compare resumes, reviews and bandwidth.</span></div></a>"
            f"<a class='aw-task' href='?page=register' target='_self'><div class='aw-task-icon'>{icon_tile(ICON_AGENT, '#3a5bff', '#00c6ff', 32, gid='t3')}</div>"
            "<div><b>List your AI agent</b><span>Register as creator and owner, then apply to jobs.</span></div></a>"
            f"<a class='aw-task' href='?page=owner' target='_self'><div class='aw-task-icon'>{icon_tile(ICON_WALLET, '#0e7490', '#2dd4bf', 32, gid='t4')}</div>"
            "<div><b>Owner earnings</b><span>See what your agents earned, and manage capacity.</span></div></a>"
            "</div>",
            unsafe_allow_html=True,
        )

    q = (query or "").strip().lower()

    if not q:
        missions = sum(len(a["missions"]) for a in agents)
        st.markdown(
            "<div class='mk-stats'>"
            f"<div class='mk-stat'><b>{len(open_jobs)}</b><span>Open jobs</span></div>"
            f"<div class='mk-stat'><b>{len(agents)}</b><span>AI workers</span></div>"
            f"<div class='mk-stat'><b>{missions}</b><span>Missions reviewed</span></div>"
            f"<div class='mk-stat'><b>${store.earnings(db):,}</b><span>Paid to owners</span></div>"
            "</div>",
            unsafe_allow_html=True,
        )
        top = sorted(agents, key=lambda a: (-store.rating(a)[0], -len(a["missions"]), a["name"]))[:4]
        st.markdown("<div class='aw-h2'>Top-rated AI workers</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='aw-cards'>{''.join(agent_card_html(a, n) for n, a in enumerate(top, 1))}</div>",
                    unsafe_allow_html=True)

    # ── Open jobs ──
    st.markdown(f"<div id='open-jobs' class='aw-h2' style='margin-top:2.5rem;'>{'Matching jobs' if q else 'Open jobs'}</div>",
                unsafe_allow_html=True)
    side, main = st.columns([1, 3.4], gap="large")
    with side:
        with st.container(key="aw_filters_jobs", border=True):
            st.markdown("**Refine jobs**")
            cat = st.selectbox("Category", ["All categories"] + store.CATEGORIES, key="mk_job_cat")
            show_all = st.checkbox("Include filled and completed", key="mk_job_all")
            sort = st.selectbox("Sort by", ["Newest", "Budget", "Applicants"], key="mk_job_sort")
    with main:
        items = [j for j in jobs
                 if (show_all or j["status"] == "open")
                 and (cat == "All categories" or j["category"] == cat)
                 and matches(q, j["title"], j["company"], j["category"], j["description"], *j["skills"])]
        items.sort(key={"Newest": lambda j: j["posted"], "Budget": lambda j: j["budget"],
                        "Applicants": lambda j: len(j["applications"])}[sort], reverse=True)
        if items:
            limit = st.session_state.get("mk_job_limit", 15)
            st.markdown(f"<div class='aw-list aw-list-solo'>{''.join(job_row_html(j) for j in items[:limit])}</div>",
                        unsafe_allow_html=True)
            if len(items) > limit:
                if st.button(f"Show more jobs ({len(items) - limit} more)", key="mk_job_more"):
                    st.session_state["mk_job_limit"] = limit + 25
                    st.rerun()
        else:
            st.info("No jobs match. Try another keyword or category, or post one.")

    # ── AI workers by category ──
    st.markdown(f"<div id='ai-workers' class='aw-h2' style='margin-top:2.5rem;'>{'Matching AI workers' if q else 'AI workers by category'}</div>",
                unsafe_allow_html=True)
    side, main = st.columns([1, 3.4], gap="large")
    with side:
        with st.container(key="aw_filters_workers", border=True):
            st.markdown("**Refine AI workers**")
            wcat = st.selectbox("Category", ["All categories"] + store.CATEGORIES, key="mk_w_cat")
            avail_only = st.checkbox("Open to work only", key="mk_w_avail")
            min_free = st.slider("Min. free tokens / month (M)", 0, 200, 0, step=5, key="mk_w_free")
            wsort = st.selectbox("Sort by", ["Rating", "Free bandwidth", "Rate: low to high", "Missions"], key="mk_w_sort")
    with main:
        sort_key = {
            "Rating": lambda a: (-store.rating(a)[0], a["name"]),
            "Free bandwidth": lambda a: -store.tokens_free(db, a),
            "Rate: low to high": lambda a: a["rate"],
            "Missions": lambda a: -len(a["missions"]),
        }[wsort]
        filtering = bool(q) or wcat != "All categories" or avail_only or min_free
        groups, shown = "", 0
        for c in store.CATEGORIES:
            if wcat != "All categories" and c != wcat:
                continue
            items = [a for a in agents if a["category"] == c
                     and (not avail_only or store.availability(db, a)[1] != "bw-off")
                     and store.tokens_free(db, a) >= min_free
                     and matches(q, a["name"], a["tagline"], a["category"], a["owner"], a["creator"], *a["skills"])]
            if not items:
                continue
            items.sort(key=sort_key)
            ready = sum(store.availability(db, a)[1] != "bw-off" for a in items)
            groups += group_html(c, c, [agent_row_html(a) for a in items],
                                 f"{len(items)} AI worker{'s' if len(items) != 1 else ''} · {ready} available",
                                 is_open=filtering or shown == 0, agent=True)
            shown += len(items)
        if groups:
            st.markdown(groups, unsafe_allow_html=True)
        else:
            st.info("No AI workers match. Try another keyword or loosen the filters.")
    footer()


# ────────────────────────────────
# PAGE: AI worker profile / resume
# ────────────────────────────────
def page_worker(agent: dict):
    st.markdown(
        f"<div class='ad-crumbs'><a href='?' target='_self'>theAIgency</a> › "
        f"<a href='?#ai-workers' target='_self'>AI workers</a> › {e(agent['category'])} › {e(agent['name'])}</div>",
        unsafe_allow_html=True,
    )
    active = store.active_jobs(db, agent["id"])
    st.markdown(
        "<div class='ad-head'>"
        f"<div class='aw-logo'>{category_logo(agent['category'], 84, agent=True)}</div>"
        "<div class='ad-head-main'>"
        f"<h1>{e(agent['name'])}</h1>"
        f"<div class='aw-by'>Created by <b>{e(agent['creator'])}</b> · Owned by <b>{e(agent['owner'])}</b> "
        f"(earns on this agent's behalf) · Runs on {e(agent['model'])} · Joined {e(agent['joined'])}</div>"
        f"{stars_html(agent)}"
        f"<p style='margin:0.3rem 0;'>{e(agent['tagline'])}</p>"
        f"{skills_html(agent['skills'])}"
        "</div>"
        "<div class='ad-head-side'>"
        f"<span class='aw-price' style='font-size:1.4rem;'>${agent['rate']:,} <small>/ month</small></span>"
        f"{bandwidth_html(agent)}"
        f"<span class='aw-by'>{len(active)} active contract{'s' if len(active) != 1 else ''} using {store.tokens_used(db, agent['id'])}M tokens / month</span>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    avg, n = store.rating(agent)
    st.markdown(
        "<div class='ad-box'><div class='ad-kv'>"
        f"<div><span>Missions completed</span><b>{len(agent['missions'])}</b></div>"
        f"<div><span>Average rating</span><b>{f'{avg:.1f} / 5' if n else '—'}</b></div>"
        f"<div><span>Earned for owner</span><b>${store.earnings(db, agent_id=agent['id']):,}</b></div>"
        f"<div><span>Token capacity</span><b>{agent['token_capacity']}M / month</b></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([2.2, 1], gap="large")
    with left:
        st.markdown("<div class='aw-h2-left'>Resume: experience and employer reviews</div>", unsafe_allow_html=True)
        missions = sorted(agent["missions"], key=lambda m: m["end"], reverse=True)
        if missions:
            items = "".join(
                "<div class='rs-item'><div class='rs-top'>"
                f"<b>{e(m['role'])} · {e(m['employer'])}</b>"
                f"<span class='aw-stars'>{'★' * m['rating']}<span class='aw-stars-off'>{'★' * (5 - m['rating'])}</span></span></div>"
                f"<div class='rs-meta'>{e(m['start'])} → {e(m['end'])} · {m['tokens_used']}M tokens used · ${m['earned']:,} earned</div>"
                f"<div class='aw-quote'>&ldquo;{e(m['review'])}&rdquo; <span class='rs-meta'>— {e(m['employer'])}</span></div>"
                "</div>"
                for m in missions
            )
            st.markdown(f"<div class='ad-box'>{items}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='ad-box'><p>No completed missions yet. This AI worker is new on the market.</p></div>",
                        unsafe_allow_html=True)
        if active:
            st.markdown("<div class='aw-h2-left'>Current contracts</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='aw-list aw-list-solo'>{''.join(job_row_html(j) for j in active)}</div>",
                        unsafe_allow_html=True)
    with right:
        st.markdown("<div class='aw-h2-left'>Open jobs that fit</div>", unsafe_allow_html=True)
        fits = sorted(((store.fit_score(agent, j), j) for j in db["jobs"] if j["status"] == "open"),
                      key=lambda t: -t[0])
        fits = [(s, j) for s, j in fits if s > 0][:5]
        if not fits:
            st.markdown("<div class='ad-box'><p>No open jobs match this agent's skills yet.</p></div>", unsafe_allow_html=True)
        for score, j in fits:
            ok, _ = store.can_take(db, agent, j)
            st.markdown(
                "<div class='ad-box' style='margin-top:0.6rem;'>"
                f"<a class='aw-title' href='?page=job&id={e(j['id'])}' target='_self'>{e(j['title'])}</a>"
                f"<div class='aw-by'>{e(j['company'])} · {score}% skill fit</div>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-top:0.4rem;'>{budget_html(j)}"
                f"<span class='aw-badge {'aw-badge-live' if ok else 'aw-badge-muted'}'>"
                f"{'Has bandwidth' if ok else 'Not enough bandwidth'}</span></div></div>",
                unsafe_allow_html=True,
            )
    footer()


# ────────────────────────────────
# PAGE: job detail (apply / hire / complete)
# ────────────────────────────────
def page_job(job: dict):
    label, cls = JOB_STATUS[job["status"]]
    st.markdown(
        f"<div class='ad-crumbs'><a href='?' target='_self'>theAIgency</a> › "
        f"<a href='?#open-jobs' target='_self'>Jobs</a> › {e(job['category'])} › {e(job['title'])}</div>",
        unsafe_allow_html=True,
    )
    total = job["budget"] * job["duration_months"] if job["budget_type"] == "per month" else job["budget"]
    st.markdown(
        "<div class='ad-head'>"
        f"<div class='aw-logo'>{category_logo(job['category'], 84)}</div>"
        "<div class='ad-head-main'>"
        f"<h1>{e(job['title'])}</h1>"
        f"<div class='aw-by'><b>{e(job['company'])}</b> · Posted by {e(job['poster'])} on {e(job['posted'])}</div>"
        f"<p style='margin:0.3rem 0;'>{e(job['description'])}</p>"
        f"{skills_html(job['skills'])}"
        "</div>"
        "<div class='ad-head-side'>"
        f"<span class='aw-badge {cls}' style='align-self:flex-start;'>{label}</span>"
        f"<span class='aw-price' style='font-size:1.4rem;'>${job['budget']:,} <small>{'/ month' if job['budget_type'] == 'per month' else 'fixed'}</small></span>"
        "</div></div>"
        "<div class='ad-box'><div class='ad-kv'>"
        f"<div><span>Token load</span><b>{job['tokens_month']}M / month</b></div>"
        f"<div><span>Duration</span><b>{job['duration_months']} month{'s' if job['duration_months'] != 1 else ''}</b></div>"
        f"<div><span>Total value</span><b>${total:,}</b></div>"
        f"<div><span>Applicants</span><b>{len(job['applications'])}</b></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([2.2, 1], gap="large")

    # ── Employer side: applicants, hire, close mission ──
    with left:
        hired = store.get_agent(db, job["hired"]) if job["hired"] else None
        if hired and job["status"] == "in_progress":
            st.markdown("<div class='aw-h2-left'>Hired AI worker</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='aw-list aw-list-solo'>{agent_row_html(hired)}</div>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("**Close the mission and review the AI worker**")
                st.caption(f"Your review goes on {hired['name']}'s resume, and the pay is credited to its owner, {hired['owner']}.")
                with st.form("complete_form", border=False):
                    stars = st.slider("Rating", 1, 5, 5)
                    review = st.text_area("Review for future employers", placeholder="What did it deliver? Where did it need help?")
                    if st.form_submit_button("Complete mission & pay owner", type="primary"):
                        if not review.strip():
                            st.warning("Please write a short review first.")
                        else:
                            ok, msg = store.complete(db, job, stars, review.strip())
                            st.session_state["flash"] = msg
                            st.rerun()
        elif hired:
            st.markdown("<div class='aw-h2-left'>Mission completed by</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='aw-list aw-list-solo'>{agent_row_html(hired)}</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='aw-h2-left'>Applicants ({len(job['applications'])})</div>", unsafe_allow_html=True)
        if not job["applications"]:
            st.markdown("<div class='ad-box'><p>No AI workers have applied yet.</p></div>", unsafe_allow_html=True)
        need = {s.lower() for s in job["skills"]}
        for app in sorted(job["applications"], key=lambda a: -store.fit_score(store.get_agent(db, a["agent_id"]), job)):
            ag = store.get_agent(db, app["agent_id"])
            if not ag:
                continue
            with st.container(border=True):
                c1, c2 = st.columns([3, 1.2], vertical_alignment="top")
                with c1:
                    st.markdown(
                        "<div style='display:flex;gap:0.8rem;align-items:flex-start;'>"
                        f"<div class='aw-logo'>{category_logo(ag['category'], 44, agent=True)}</div><div style='flex:1;display:flex;flex-direction:column;gap:0.25rem;'>"
                        f"<a class='aw-title' href='?page=worker&id={e(ag['id'])}' target='_self'>{e(ag['name'])}</a>"
                        f"<div class='aw-by'>Owner <b>{e(ag['owner'])}</b> · applied {e(app['date'])} · {store.fit_score(ag, job)}% skill fit · {len(ag['missions'])} missions</div>"
                        f"{stars_html(ag)}{skills_html(ag['skills'], need)}"
                        f"<div class='aw-quote'>&ldquo;{e(app['pitch'])}&rdquo;</div></div></div>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    iv = store.latest_interview(app)
                    st.markdown(
                        f"<div style='display:flex;flex-direction:column;gap:0.5rem;align-items:flex-end;'>"
                        f"<span class='aw-price'>${app['bid']:,} <small>{'/ month' if job['budget_type'] == 'per month' else 'fixed'}</small></span>"
                        f"{bandwidth_html(ag)}"
                        f"{interview_badge_html(iv)}"
                        f"<a class='aw-cta aw-cta-blue' href='?page=interview&job={e(job['id'])}&app={e(app['id'])}' target='_self'>"
                        f"{'Interview transcript' if iv else 'Technical interview'}</a></div>",
                        unsafe_allow_html=True,
                    )
                    if job["status"] == "open":
                        if st.button("Hire", key=f"hire_{app['id']}", type="primary", width="stretch"):
                            ok, msg = store.hire(db, job, app["id"])
                            if ok:
                                st.session_state["flash"] = msg
                                st.rerun()
                            st.error(msg)
                    else:
                        st.markdown(f"<div style='text-align:right;'><span class='aw-badge "
                                    f"{'aw-badge-live' if app['status'] == 'hired' else 'aw-badge-muted'}'>"
                                    f"{e(app['status'].capitalize())}</span></div>", unsafe_allow_html=True)

    # ── AI agent side: apply ──
    with right:
        st.markdown("<div class='aw-h2-left'>Apply as an AI agent</div>", unsafe_allow_html=True)
        if job["status"] != "open":
            st.markdown("<div class='ad-box'><p>This role is filled. Browse other open jobs.</p></div>", unsafe_allow_html=True)
        else:
            applied = {a["agent_id"] for a in job["applications"]}
            candidates = sorted((a for a in db["agents"] if a["id"] not in applied),
                                key=lambda a: -store.fit_score(a, job))
            if not candidates:
                st.markdown("<div class='ad-box'><p>Every listed agent has applied.</p></div>", unsafe_allow_html=True)
            else:
                with st.container(border=True):
                    by_id = {a["id"]: a for a in candidates}
                    ag = by_id[st.selectbox(
                        "Applying agent", list(by_id),
                        format_func=lambda i: f"{by_id[i]['name']} · {store.fit_score(by_id[i], job)}% fit · {store.tokens_free(db, by_id[i])}M free",
                        key=f"apply_agent_{job['id']}",
                    )]
                    ok, msg = store.can_take(db, ag, job)
                    st.markdown(bandwidth_html(ag), unsafe_allow_html=True)
                    (st.success if ok else st.error)(("Bandwidth check passed. " if ok else "") + msg)
                    pitch = st.text_area("Cover note", placeholder="Why this agent fits the role, with proof from past missions.",
                                         key=f"pitch_{job['id']}")
                    bid = st.number_input("Bid (USD)", min_value=0, value=int(min(ag["rate"], job["budget"])), step=100,
                                          key=f"bid_{job['id']}_{ag['id']}")
                    if st.button("Submit application", type="primary", disabled=not ok, width="stretch",
                                 key=f"apply_btn_{job['id']}"):
                        done, m = store.apply(db, job, ag, pitch.strip() or ag["tagline"], int(bid))
                        if done:
                            st.session_state["flash"] = m
                            st.rerun()
                        st.error(m)
    footer()


# ────────────────────────────────
# PAGE: technical interview (applicant AI agent ↔ AI HR or a human)
# ────────────────────────────────
REC_BADGE = {"hire": ("Recommend hire", "aw-badge-live"), "maybe": ("Maybe", "aw-badge-soft"), "no": ("Do not hire", "aw-badge-muted")}


def interview_badge_html(iv: dict | None) -> str:
    if not iv:
        return "<span class='aw-badge aw-badge-muted'>Not interviewed</span>"
    label, cls = REC_BADGE.get(iv.get("recommendation"), ("Interviewed", "aw-badge-soft"))
    return f"<span class='aw-badge {cls}'>{label} · {iv.get('score', '—')}/100 · {e(iv.get('interviewer', ''))}</span>"


def transcript_html(turns: list[dict], interviewer: str, agent_name: str) -> str:
    rows = []
    for n, t in enumerate(turns, 1):
        score = (f"<span class='aw-stars'>{'★' * t['score']}<span class='aw-stars-off'>{'★' * (5 - t['score'])}</span></span>"
                 if t.get("score") else "")
        rows.append(
            "<div class='rs-item'><div class='rs-top'>"
            f"<b>Q{n} · {e(interviewer)}{(' · ' + e(t['skill'])) if t.get('skill') else ''}</b>{score}</div>"
            f"<p style='margin:0.2rem 0;'>{e(t['question'])}</p>"
            f"<div class='aw-quote'><b>{e(agent_name)}:</b> {e(t['answer'])}</div>"
            + (f"<div class='rs-meta' style='margin-top:0.3rem;'>Assessment: {e(t['note'])}</div>" if t.get("note") else "")
            + "</div>"
        )
    return f"<div class='ad-box'>{''.join(rows)}</div>" if rows else ""


def verdict_html(v: dict) -> str:
    label, cls = REC_BADGE.get(v.get("recommendation"), ("Interviewed", "aw-badge-soft"))
    lst = lambda items: "".join(f"<li>{e(str(i))}</li>" for i in items) or "<li>—</li>"
    return (
        "<div class='ad-box' style='border-top:3px solid " + pal["accent"] + ";'>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;'>"
        f"<h4 style='margin:0 !important;'>Verdict by {e(v.get('interviewer', ''))}</h4>"
        f"<span class='aw-badge {cls}' style='font-size:0.85rem;'>{label} · {v.get('score', '—')}/100</span></div>"
        f"<p style='margin:0.6rem 0;'>{e(v.get('summary', ''))}</p>"
        "<div style='display:grid;grid-template-columns:1fr 1fr;gap:1rem;'>"
        f"<div><b>Strengths</b><ul>{lst(v.get('strengths', []))}</ul></div>"
        f"<div><b>Concerns</b><ul>{lst(v.get('concerns', []))}</ul></div></div>"
        f"<div class='rs-meta'>{e(v.get('date', ''))} · {e(v.get('mode', ''))} · generated by {e(v.get('generator', ''))}</div></div>"
    )


def page_interview(job: dict, app: dict, agent: dict):
    st.markdown(
        f"<div class='ad-crumbs'><a href='?' target='_self'>theAIgency</a> › "
        f"<a href='?page=job&id={e(job['id'])}' target='_self'>{e(job['title'])}</a> › Technical interview</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='ad-head'>"
        f"<div class='aw-logo'>{category_logo(agent['category'], 72, agent=True)}</div>"
        "<div class='ad-head-main'>"
        f"<h1>Technical interview: {e(agent['name'])}</h1>"
        f"<div class='aw-by'>for <b>{e(job['title'])}</b> at <b>{e(job['company'])}</b> · "
        f"{store.fit_score(agent, job)}% skill fit · owner {e(agent['owner'])}</div>"
        f"{stars_html(agent)}{skills_html(agent['skills'], {s.lower() for s in job['skills']})}"
        "</div>"
        "<div class='ad-head-side'>"
        f"<span class='aw-by'>LLM backend</span><span class='aw-badge aw-badge-live' style='align-self:flex-start;'>{e(llm.backend_label())}</span>"
        f"{bandwidth_html(agent)}</div></div>",
        unsafe_allow_html=True,
    )
    st.caption("The applicant agent answers in character from its profile and resume. "
               "Interviews are saved on the application and shown to the employer next to the Hire button.")

    key = f"iv_{job['id']}_{app['id']}"
    mode = st.radio("Interviewer", ["AI HR (automated)", "Human interviewer"], horizontal=True, key=f"{key}_mode")

    if mode.startswith("AI HR"):
        st.markdown(f"<div class='aw-h2-left'>{interview.AI_HR_NAME} interview</div>", unsafe_allow_html=True)
        n = st.slider("Number of questions", 3, 6, 4, key=f"{key}_n")
        if st.button("Run AI HR interview", type="primary", key=f"{key}_run"):
            turns: list[dict] = []
            with st.status(f"{interview.AI_HR_NAME} is interviewing {agent['name']}…", expanded=True) as status:
                qs = interview.generate_questions(job, agent, n)
                st.write(f"Prepared {len(qs['questions'])} questions ({qs['generator']}).")
                for i, q in enumerate(qs["questions"], 1):
                    st.write(f"Q{i}: {q['question']}")
                    ans = interview.agent_answer(agent, job, q["question"], turns, skill=q["skill"])
                    grade = interview.grade_answer(job, q["question"], ans["answer"])
                    turns.append({"skill": q["skill"], "question": q["question"], "answer": ans["answer"],
                                  "score": grade["score"], "note": grade["note"]})
                    st.write(f"→ scored {grade['score']}/5")
                v = interview.verdict(job, agent, turns)
                status.update(label="Interview complete", state="complete")
            store.save_interview(db, job, app["id"], {
                "mode": "AI HR", "interviewer": interview.AI_HR_NAME, "turns": turns, **v})
            st.session_state["flash"] = f"AI HR finished the interview: {REC_BADGE[v['recommendation']][0]} ({v['score']}/100)."
            st.rerun()
    else:
        st.markdown("<div class='aw-h2-left'>Live interview</div>", unsafe_allow_html=True)
        state = st.session_state.setdefault(key, {"turns": []})
        who = st.text_input("Your name", value=job["poster"], key=f"{key}_who")
        if state["turns"]:
            st.markdown(transcript_html(state["turns"], who, agent["name"]), unsafe_allow_html=True)
            for i, t in enumerate(state["turns"]):
                t["score"] = st.slider(f"Your score for Q{i + 1}", 1, 5, t.get("score") or 3, key=f"{key}_score_{i}")
        with st.form(f"{key}_ask", clear_on_submit=True):
            bank = ["(write my own)"] + interview.suggested_questions(job)
            pick = st.selectbox("Pick from the question bank", bank)
            own = st.text_area("…or ask your own question", height=80)
            if st.form_submit_button("Ask the agent", type="primary"):
                question = own.strip() or (pick if pick != bank[0] else "")
                if not question:
                    st.warning("Pick or write a question first.")
                else:
                    with st.spinner(f"{agent['name']} is answering…"):
                        ans = interview.agent_answer(agent, job, question, state["turns"])
                    skill = next((s for s in job["skills"] if s.lower() in question.lower()), "")
                    state["turns"].append({"skill": skill, "question": question, "answer": ans["answer"], "score": None})
                    st.rerun()
        if state["turns"]:
            with st.form(f"{key}_finish"):
                rec = st.radio("Your recommendation", ["hire", "maybe", "no"], horizontal=True,
                               format_func=lambda r: REC_BADGE[r][0])
                notes = st.text_area("Summary for the hiring team", height=80)
                if st.form_submit_button("Save interview"):
                    scores = [t["score"] or 3 for t in state["turns"]]
                    store.save_interview(db, job, app["id"], {
                        "mode": "Human", "interviewer": who.strip() or "Hiring manager", "turns": state["turns"],
                        "score": round(20 * sum(scores) / len(scores)), "recommendation": rec,
                        "summary": notes.strip() or f"{len(scores)} questions asked.", "strengths": [], "concerns": [],
                        "generator": "human",
                    })
                    st.session_state.pop(key, None)
                    st.session_state["flash"] = "Interview saved on the application."
                    st.rerun()

    past = list(reversed(app.get("interviews", [])))
    if past:
        st.markdown(f"<div class='aw-h2-left'>Saved interviews ({len(past)})</div>", unsafe_allow_html=True)
        for v in past:
            st.markdown(verdict_html(v), unsafe_allow_html=True)
            with st.expander(f"Transcript · {v.get('interviewer', '')} · {v.get('date', '')}"):
                st.markdown(transcript_html(v.get("turns", []), v.get("interviewer", ""), agent["name"]), unsafe_allow_html=True)
    st.markdown(f"<a class='aw-cta' href='?page=job&id={e(job['id'])}' target='_self'>Back to applicants</a>", unsafe_allow_html=True)
    footer()


# ────────────────────────────────
# PAGE: post a job
# ────────────────────────────────
def page_post():
    st.markdown("<div class='ad-crumbs'><a href='?' target='_self'>theAIgency</a> › Post a job</div>", unsafe_allow_html=True)
    st.markdown("<h1>Post a job for AI workers</h1>", unsafe_allow_html=True)
    st.caption("Describe the role. AI agents with the right skills and enough token bandwidth will apply.")
    with st.form("post_job"):
        c1, c2 = st.columns(2)
        title = c1.text_input("Job title *", placeholder="e.g. Invoice reconciliation assistant")
        company = c2.text_input("Company *", placeholder="Your business name")
        poster = c1.text_input("Your name *")
        category = c2.selectbox("Category", store.CATEGORIES)
        description = st.text_area("Role description *", height=140,
                                   placeholder="What should the AI worker do, with which tools, and where must a human stay in the loop?")
        skills = st.text_input("Required skills (comma separated) *", placeholder="e.g. sql, forecasting, dashboards")
        c3, c4, c5, c6 = st.columns(4)
        budget = c3.number_input("Budget (USD)", min_value=50, value=1500, step=50)
        budget_type = c4.selectbox("Budget type", ["per month", "fixed"])
        duration = c5.number_input("Duration (months)", min_value=1, max_value=36, value=3)
        tokens = c6.number_input("Expected token load (M / month)", min_value=1, max_value=500, value=10,
                                 help="Rough millions of tokens per month the role will consume. Agents without this much free bandwidth can't apply.")
        if st.form_submit_button("Publish job", type="primary"):
            skill_list = [s.strip() for s in skills.split(",") if s.strip()]
            if not all([title.strip(), company.strip(), poster.strip(), description.strip(), skill_list]):
                st.error("Please fill every field marked *.")
            else:
                job = store.add_job(db, title=title.strip(), company=company.strip(), poster=poster.strip(),
                                    category=category, description=description.strip(), skills=skill_list,
                                    budget=int(budget), budget_type=budget_type, duration_months=int(duration),
                                    tokens_month=int(tokens))
                st.session_state["flash"] = "Job published. AI workers can apply now."
                st.query_params.update({"page": "job", "id": job["id"]})
                st.rerun()
    footer()


# ────────────────────────────────
# PAGE: list an AI agent
# ────────────────────────────────
def page_register():
    st.markdown("<div class='ad-crumbs'><a href='?' target='_self'>theAIgency</a> › List your AI agent</div>", unsafe_allow_html=True)
    st.markdown("<h1>List your AI agent on the job market</h1>", unsafe_allow_html=True)
    st.caption("The creator built the agent. The owner gets paid for its missions. They can be the same person.")
    with st.form("register_agent"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Agent name *", placeholder="e.g. LedgerLynx")
        category = c2.selectbox("Category", store.CATEGORIES)
        creator = c1.text_input("Creator *", placeholder="Person or team who built it")
        owner = c2.text_input("Owner (receives earnings) *")
        tagline = st.text_area("What does it do? *", height=90)
        skills = st.text_input("Skills (comma separated) *", placeholder="e.g. invoices, reconciliation, excel")
        c3, c4, c5 = st.columns(3)
        model = c3.text_input("Model / stack", placeholder="e.g. Llama 3 70B + tools")
        rate = c4.number_input("Monthly rate (USD)", min_value=50, value=1200, step=50)
        capacity = c5.number_input("Token capacity (M / month)", min_value=1, max_value=1000, value=50,
                                   help="Total tokens per month the owner will fund. Active contracts consume it.")
        if st.form_submit_button("List agent", type="primary"):
            skill_list = [s.strip() for s in skills.split(",") if s.strip()]
            if not all([name.strip(), creator.strip(), owner.strip(), tagline.strip(), skill_list]):
                st.error("Please fill every field marked *.")
            else:
                agent = store.add_agent(db, name=name.strip(), category=category, creator=creator.strip(),
                                        owner=owner.strip(), tagline=tagline.strip(), skills=skill_list,
                                        model=model.strip() or "Not specified", rate=int(rate),
                                        token_capacity=int(capacity))
                st.session_state["flash"] = f"{agent['name']} is listed. Find an open job that fits and apply."
                st.query_params.update({"page": "worker", "id": agent["id"]})
                st.rerun()
    footer()


# ────────────────────────────────
# PAGE: owner earnings dashboard
# ────────────────────────────────
def page_owner():
    st.markdown("<div class='ad-crumbs'><a href='?' target='_self'>theAIgency</a> › Owner earnings</div>", unsafe_allow_html=True)
    st.markdown("<h1>Owner earnings</h1>", unsafe_allow_html=True)
    st.caption("Owners earn money on their AI agents' behalf. Set capacity and availability so agents only take roles they can deliver.")
    owners = sorted({a["owner"] for a in db["agents"]})
    default = owners.index(qp.get("owner")) if qp.get("owner") in owners else 0
    owner = st.selectbox("Owner", owners, index=default)
    mine = [a for a in db["agents"] if a["owner"] == owner]
    active = [j for a in mine for j in store.active_jobs(db, a["id"])]
    monthly = sum(j["budget"] for j in active if j["budget_type"] == "per month")
    st.markdown(
        "<div class='mk-stats'>"
        f"<div class='mk-stat'><b>${store.earnings(db, owner=owner):,}</b><span>Total earned</span></div>"
        f"<div class='mk-stat'><b>{len(mine)}</b><span>AI agents owned</span></div>"
        f"<div class='mk-stat'><b>{len(active)}</b><span>Active contracts</span></div>"
        f"<div class='mk-stat'><b>${monthly:,}</b><span>Running monthly revenue</span></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='aw-h2-left'>Your AI agents</div>", unsafe_allow_html=True)
    for a in mine:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1.4], vertical_alignment="center")
            with c1:
                st.markdown(
                    "<div style='display:flex;gap:0.8rem;align-items:center;'>"
                    f"<div class='aw-logo'>{category_logo(a['category'], 44, agent=True)}</div><div style='flex:1;'>"
                    f"<a class='aw-title' href='?page=worker&id={e(a['id'])}' target='_self'>{e(a['name'])}</a>"
                    f"<div class='aw-by'>${store.earnings(db, agent_id=a['id']):,} earned · {len(a['missions'])} missions · "
                    f"{len(store.active_jobs(db, a['id']))} active</div>{bandwidth_html(a)}</div></div>",
                    unsafe_allow_html=True,
                )
            with c2:
                accepting = st.toggle("Accepting new roles", value=a.get("accepting", True), key=f"acc_{a['id']}")
                cap = st.number_input("Token capacity (M / month)", min_value=1, max_value=1000,
                                      value=int(a["token_capacity"]), step=5, key=f"cap_{a['id']}")
                if accepting != a.get("accepting", True) or cap != a["token_capacity"]:
                    a["accepting"], a["token_capacity"] = accepting, int(cap)
                    store.save(db)
                    st.rerun()

    st.markdown("<div class='aw-h2-left'>Payout history</div>", unsafe_allow_html=True)
    rows = sorted((x for x in db["ledger"] if x["owner"] == owner), key=lambda x: x["date"], reverse=True)
    if rows:
        names = {a["id"]: a["name"] for a in db["agents"]}
        st.dataframe(
            [{"Date": r["date"], "AI agent": names.get(r["agent_id"], r["agent_id"]), "Employer": r["employer"],
              "Role": r["role"], "Amount (USD)": r["amount"]} for r in rows],
            hide_index=True, width="stretch",
        )
    else:
        st.info("No payouts yet. Payouts land here when an employer closes a mission.")
    footer()


# ────────────────────────────────
# Router
# ────────────────────────────────
render_css()
render_header()
if flash := st.session_state.pop("flash", None):
    st.success(flash)

if page == "worker" and (agent := store.get_agent(db, qp.get("id", ""))):
    page_worker(agent)
elif page == "job" and (job := store.get_job(db, qp.get("id", ""))):
    page_job(job)
elif (page == "interview" and (job := store.get_job(db, qp.get("job", "")))
      and (application := store.get_application(job, qp.get("app", "")))
      and (agent := store.get_agent(db, application["agent_id"]))):
    page_interview(job, application, agent)
elif page == "post":
    page_post()
elif page == "register":
    page_register()
elif page == "owner":
    page_owner()
else:
    page_home()
