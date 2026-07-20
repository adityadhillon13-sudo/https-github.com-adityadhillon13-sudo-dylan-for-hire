"""
Builds blueline_pitch_deck.html — 12-slide deck, v3.
Full rebuild: larger fonts, color system, system-agnostic, all feedback addressed.

[DEPRECATED 2026-07-02, Round 6 audit — DO NOT RUN EXPECTING A LIVE-DECK REFRESH]
This script's output was already known (09_GO_LIVE_READINESS.md KNOWN GAP #7,
2026-07-01) to write to the wrong filename (blueline_pitch_deck.html instead
of the real, presented dylan_for_hire_pitch_deck.html). Round 6 checked the
content risk of just repointing OUT and found it's worse than the filename
mismatch alone: this script's hardcoded HTML has NO embedded audio (0 base64
blocks vs. 12 in the real file) and predates the v3.0 24/7 real-time layer —
running it and overwriting the real file would silently regress a better,
audio-narrated, current deck to a worse, silent, stale one. OUT is redirected
below to a clearly-labeled path so this can never happen by accident, even if
someone runs this script not knowing the above. To actually refresh the live
deck: hand-edit dylan_for_hire_pitch_deck.html directly, or ask for a fresh
rebuild that starts from its current content (including audio) rather than
from this file's stale hardcoded HTML. See DYLAN_AUDIT_2026-07-01_FULL.md
Round 6 and 09_GO_LIVE_READINESS.md KNOWN GAPS.
"""
import os

# [FIX 2026-07-02] Was ~/Downloads/BlueLine/blueline_pitch_deck.html — that
# alone was already wrong (see docstring above). Redirected here rather than
# to the real dylan_for_hire_pitch_deck.html because this script's content is
# stale and would regress the real file if it were ever run again.
OUT = os.path.expanduser("~/Downloads/BlueLine/DEPRECATED_DO_NOT_USE_blueline_pitch_deck.html")

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BlueLine AI Staffing — Pitch Deck</title>
<style>
/* ── DESIGN TOKENS ── */
:root{
  --bg:#060913; --surface:#0d1126; --card:#111828; --card2:#0d1a2e; --border:#1e2d45;
  --blue:#2563eb; --blue-l:#3b82f6;
  /* LOSS / PAIN / NEGATIVE = RED */
  --red:#ef4444; --red-bg:#1c0a0a; --red-border:#7f1d1d;
  /* GAIN / AI / POSITIVE = GREEN */
  --green:#10b981; --green-bg:#0a2018; --green-border:#065f46;
  /* WARNING / HIDDEN COST = AMBER */
  --amber:#f59e0b; --amber-bg:#1c1205; --amber-border:#78350f;
  /* NEUTRAL DATA = BLUE */
  --blue-bg:#0d1a2e; --blue-border:#1d4ed8;
  /* PREMIUM / PRICING = PURPLE */
  --purple:#8b5cf6; --purple-bg:#0d0a1e; --purple-border:#3b1d6e;
  --text:#f1f5f9; --muted:#64748b; --dim:#334155;
}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{height:100%;overflow:hidden;background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:15px;}

/* ── TOPBAR ── */
.topbar{height:52px;display:flex;align-items:center;justify-content:space-between;
  padding:0 24px;background:var(--surface);border-bottom:1px solid var(--border);
  position:relative;z-index:10;flex-shrink:0;}
.tb-left{display:flex;align-items:center;gap:12px;}
.tb-logo{width:32px;height:32px;border-radius:8px;background:var(--blue);
  display:flex;align-items:center;justify-content:center;font-size:16px;}
.tb-title{font-size:15px;font-weight:700;}
.tb-sub{font-size:12px;color:var(--muted);margin-left:6px;}
.tb-controls{display:flex;align-items:center;gap:8px;}
.ctrl-btn{border:none;border-radius:7px;padding:7px 16px;font-size:13px;
  font-weight:600;cursor:pointer;transition:all .15s;}
.btn-blue{background:var(--blue);color:#fff;}
.btn-blue:hover{background:var(--blue-l);}
.btn-ghost{background:var(--card);color:var(--muted);border:1px solid var(--border);}
.btn-ghost.active{background:#1e2d45;color:var(--text);border-color:var(--blue);}
.slide-counter{font-size:12px;color:var(--muted);padding:0 8px;}
.progress-bar{height:3px;background:var(--border);}
.progress-fill{height:100%;background:var(--blue);transition:width .5s ease;}

/* ── LAYOUT ── */
.main-area{display:flex;height:calc(100vh - 55px);overflow:hidden;}
.slide-panel{flex:1;overflow:hidden;display:flex;flex-direction:column;}
.slide-viewport{flex:1;overflow:hidden;position:relative;}
.slide{position:absolute;inset:0;padding:22px 40px 14px;display:none;
  flex-direction:column;opacity:0;transition:opacity .3s ease;overflow-y:auto;}
.slide.active{display:flex;opacity:1;}
.slide-tag{font-size:10px;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;color:var(--muted);margin-bottom:10px;}
.slide h1{font-size:38px;font-weight:800;line-height:1.12;margin-bottom:10px;}
.slide h2{font-size:27px;font-weight:700;margin-bottom:10px;}
.deck-sub{font-size:15px;color:var(--muted);margin-bottom:16px;line-height:1.6;}

/* ── NAV ── */
.nav-area{display:flex;align-items:center;justify-content:space-between;
  padding:10px 24px;background:var(--surface);border-top:1px solid var(--border);
  flex-shrink:0;}
.nav-btn{border:1px solid var(--border);background:var(--card);color:var(--muted);
  border-radius:8px;padding:8px 22px;font-size:14px;cursor:pointer;transition:all .15s;}
.nav-btn:hover:not(:disabled){border-color:var(--blue);color:var(--text);}
.nav-btn:disabled{opacity:.3;cursor:not-allowed;}
.nav-dots{display:flex;gap:5px;}
.dot{width:7px;height:7px;border-radius:50%;background:var(--dim);
  cursor:pointer;transition:all .2s;}
.dot.active{background:var(--blue);transform:scale(1.5);}

/* ── SPEAKER NOTES ── */
.notes-panel{width:320px;min-width:320px;background:var(--surface);
  border-left:1px solid var(--border);overflow-y:auto;display:none;flex-direction:column;}
.notes-panel.open{display:flex;}
.notes-header{padding:13px 18px;font-size:11px;font-weight:700;letter-spacing:1.2px;
  text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--border);
  display:flex;align-items:center;gap:6px;flex-shrink:0;}
.notes-time{display:inline-block;background:#1e2d45;color:var(--blue-l);
  font-size:11px;font-weight:700;padding:2px 10px;border-radius:12px;margin-bottom:10px;}
.notes-content{padding:14px 18px;font-size:13px;color:#94a3b8;line-height:1.7;}
.notes-content h3{font-size:13px;font-weight:700;color:var(--text);
  margin:14px 0 8px;}
.notes-content h3:first-child{margin-top:0;}
.notes-content ul{list-style:none;padding:0;}
.notes-content li{padding:3px 0 3px 16px;position:relative;}
.notes-content li::before{content:"›";position:absolute;left:0;color:var(--blue-l);}
.notes-content .exact{background:#0d1a2e;border-left:2px solid var(--blue-l);
  padding:10px 12px;border-radius:0 6px 6px 0;color:#93c5fd;font-style:italic;
  margin:10px 0;font-size:12px;line-height:1.65;}
.notes-content .warn{color:var(--amber);}

/* ── ATOMS ── */
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
.three-col{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;}
.four-col{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:13px;
  padding:16px 18px;}
.card-red{border-color:var(--red-border);background:var(--red-bg);}
.card-green{border-color:var(--green-border);background:var(--green-bg);}
.card-blue{border-color:var(--blue-border);background:var(--blue-bg);}
.card-amber{border-color:var(--amber-border);background:var(--amber-bg);}
.card-purple{border-color:var(--purple-border);background:var(--purple-bg);}
.stat{font-size:46px;font-weight:800;line-height:1;margin-bottom:5px;}
.stat.red{color:var(--red);}.stat.green{color:var(--green);}
.stat.blue{color:var(--blue-l);}.stat.amber{color:var(--amber);}
.stat.purple{color:var(--purple);}
.stat-label{font-size:13px;color:var(--muted);}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;
  font-size:11px;font-weight:700;margin:2px;}
.bdg-blue{background:#1d3a7a;color:#93c5fd;}
.bdg-green{background:#064e3b;color:#6ee7b7;}
.bdg-red{background:#7f1d1d;color:#fca5a5;}
.bdg-amber{background:#78350f;color:#fcd34d;}
.bdg-purple{background:#3b1d6e;color:#c4b5fd;}
.src{font-size:10px;color:var(--dim);font-style:italic;margin-top:7px;line-height:1.6;}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-thumb{background:var(--dim);border-radius:3px;}

/* ── SLIDE 1 ── */
.hero-metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px;}
.hero-metric{background:var(--card);border:1px solid var(--border);
  border-radius:13px;padding:18px 20px;}
.hero-tag-row{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;}
.response-table{width:100%;border-collapse:collapse;margin-top:14px;
  border-radius:12px;overflow:hidden;border:1px solid var(--border);}
.response-table th{background:var(--surface);padding:10px 16px;font-size:11px;
  font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);}
.response-table td{padding:11px 16px;font-size:14px;border-top:1px solid var(--border);}
.response-table td:first-child{color:var(--text);font-weight:500;}
.td-bad{color:var(--red);font-weight:700;}
.td-good{color:var(--green);font-weight:700;}
.td-src{font-size:11px;color:var(--dim);}

/* ── SLIDE 2 ── */
.pain-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px;margin-top:12px;}
.pain-item{background:var(--red-bg);border:1px solid var(--red-border);
  border-radius:13px;padding:18px 20px;}
.pain-icon{font-size:26px;margin-bottom:8px;}
.pain-title{font-weight:700;font-size:16px;margin-bottom:6px;color:#fca5a5;}
.pain-body{font-size:13px;color:#9ca3af;line-height:1.6;}
.vs-bar{display:flex;align-items:center;gap:0;background:#0a0f1f;
  border:1px solid var(--border);border-radius:13px;padding:16px 20px;
  margin-top:14px;}
.vs-side{flex:1;}
.vs-label{font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:1px;margin-bottom:6px;}
.vs-val{font-size:26px;font-weight:800;}
.vs-arrow{font-size:38px;color:var(--blue-l);padding:0 20px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;opacity:.7;}

/* ── SLIDE 3 ── */
.journey-flow{display:grid;grid-template-columns:repeat(6,1fr);
  gap:0;margin:14px 0 10px;position:relative;}
.journey-flow::before{content:'';position:absolute;top:24px;left:34px;
  right:34px;height:2px;background:var(--border);z-index:0;}
.j-stage{display:flex;flex-direction:column;align-items:center;
  text-align:center;position:relative;z-index:1;padding:0 4px;}
.j-num{width:48px;height:48px;border-radius:50%;display:flex;
  align-items:center;justify-content:center;font-weight:700;font-size:14px;
  border:2px solid var(--blue-l);background:var(--blue-bg);
  color:var(--blue-l);margin-bottom:8px;}
.j-title{font-size:12px;font-weight:700;margin-bottom:5px;}
.j-manual{font-size:12px;color:var(--red);font-weight:700;margin-bottom:2px;}
.j-ai{font-size:12px;color:var(--green);font-weight:700;margin-bottom:6px;}
.j-tags{display:flex;flex-wrap:wrap;gap:2px;justify-content:center;}
.j-tag{font-size:10px;padding:2px 6px;border-radius:8px;
  background:#1e2d45;color:var(--muted);}
.journey-table{margin-top:10px;border-radius:12px;overflow:hidden;
  border:1px solid var(--border);}
.jt-row{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;}
.jt-hdr .jt-cell{background:var(--surface);font-size:11px;font-weight:700;
  text-transform:uppercase;letter-spacing:.8px;color:var(--muted);}
.jt-cell{padding:10px 14px;font-size:13px;border-bottom:1px solid var(--border);
  border-right:1px solid var(--border);}
.jt-cell:last-child{border-right:none;}
.jt-row:last-child .jt-cell{border-bottom:none;font-weight:700;
  background:#0a0f1f;font-size:14px;}

/* ── SLIDE 4 ── */
.cost-table{width:100%;border-collapse:collapse;margin-top:12px;}
.cost-table th{text-align:left;padding:10px 16px;font-size:12px;font-weight:700;
  letter-spacing:1px;text-transform:uppercase;color:var(--muted);
  border-bottom:1px solid var(--border);}
.cost-table td{padding:11px 16px;font-size:14px;border-bottom:1px solid #111828;}
.cost-table .total-row td{font-weight:700;border-top:1px solid var(--border);
  border-bottom:none;font-size:15px;}
.cost-table .td-red{color:var(--red);font-weight:700;}
.cost-table .td-note{font-size:12px;color:var(--muted);}
.savings-banner{background:var(--green-bg);border:1px solid var(--green-border);
  border-radius:13px;padding:16px 22px;display:flex;justify-content:space-between;
  align-items:center;margin-top:14px;}
.savings-num{font-size:36px;font-weight:800;color:var(--green);}
.savings-label{font-size:13px;color:#4ade80;margin-top:2px;}
.downtime-header{font-size:13px;font-weight:700;color:var(--amber);
  text-transform:uppercase;letter-spacing:1px;margin:16px 0 9px;
  display:flex;align-items:center;gap:9px;}
.downtime-header::after{content:'';flex:1;height:1px;background:var(--amber-border);}
.downtime-grid{display:grid;grid-template-columns:2fr .6fr .6fr 1.8fr;
  gap:0;border:1px solid var(--amber-border);border-radius:11px;
  overflow:hidden;margin-bottom:10px;}
.dg-hdr .dg-cell{background:#1c1205;font-size:11px;font-weight:700;
  text-transform:uppercase;letter-spacing:.7px;color:#92400e;}
.dg-cell{padding:9px 14px;font-size:14px;border-bottom:1px solid #2a1a00;
  border-right:1px solid #2a1a00;}
.dg-cell:last-child{border-right:none;}
.dg-total .dg-cell{border-bottom:none;font-weight:700;background:#1c1205;}
.downtime-impact{display:grid;grid-template-columns:1fr 1fr 1fr;
  gap:10px;margin-bottom:10px;}
.dt-card{background:var(--card);border:1px solid var(--amber-border);
  border-radius:11px;padding:14px 16px;text-align:center;}
.dt-num{font-size:28px;font-weight:800;color:var(--amber);margin-bottom:3px;}
.dt-label{font-size:13px;color:var(--muted);}
.true-cost-banner{background:var(--red-bg);border:1px solid var(--red-border);
  border-radius:13px;padding:16px 22px;display:flex;
  justify-content:space-between;align-items:center;}
.tc-left{font-size:14px;color:#fca5a5;line-height:1.8;}
.tc-num{font-size:36px;font-weight:800;color:var(--red);}
.tc-vs{font-size:14px;color:var(--green);font-weight:700;margin-top:4px;}

/* ── SLIDE 5 ── */
.steps-grid{display:grid;grid-template-columns:repeat(4,1fr);
  gap:10px;margin-top:14px;}
.step-card{border-radius:13px;padding:18px 16px;border:2px solid;}
.step-card.s1{border-color:var(--green);background:var(--green-bg);}
.step-card.s2{border-color:var(--blue-l);background:var(--blue-bg);}
.step-card.s3{border-color:var(--amber);background:var(--amber-bg);}
.step-card.s4{border-color:var(--purple);background:var(--purple-bg);}
.step-num{font-size:11px;font-weight:700;letter-spacing:1px;margin-bottom:4px;}
.step-name{font-size:16px;font-weight:700;margin-bottom:8px;}
.step-body{font-size:12px;color:#9ca3af;line-height:1.6;margin-bottom:8px;}
.step-tools{font-size:11px;color:var(--dim);font-style:italic;
  border-top:1px solid rgba(255,255,255,.06);padding-top:7px;margin-top:4px;}
.step-tools strong{color:var(--muted);font-style:normal;}
.step-rationale{font-size:11px;font-weight:600;margin-top:8px;
  padding:5px 10px;border-radius:6px;background:rgba(0,0,0,.3);
  display:inline-block;}

/* ── SLIDE 6 ── */
.examples-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;
  margin-top:12px;}
.ex-pair{display:flex;flex-direction:column;gap:8px;}
.ex-label{font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:1px;margin-bottom:6px;}
.bubble{border-radius:13px;padding:13px 15px;font-size:13px;
  line-height:1.55;color:#cbd5e1;}
.bubble.bad{background:#1e2540;border:1px solid #1d4ed8;}
.bubble.good{background:#0d2e1a;border:1px solid #065f46;color:#6ee7b7;}
.ex-result{font-size:13px;font-weight:600;margin-top:5px;}
.ex-result.loss{color:var(--red);}
.ex-result.win{color:var(--green);}
.context-engine{background:var(--card);border:1px solid var(--border);
  border-radius:13px;padding:16px 18px;margin-top:12px;}
.ce-steps{display:grid;grid-template-columns:1fr 1fr 1fr;
  gap:14px;margin-top:10px;}
.ce-step{font-size:13px;color:var(--muted);line-height:1.65;}

/* ── SLIDE 7 ── */
.comp-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px;}
.comp-card{background:var(--card);border:1px solid var(--border);
  border-radius:13px;padding:16px 18px;}
.comp-icon{font-size:26px;margin-bottom:8px;}
.comp-title{font-size:15px;font-weight:700;margin-bottom:7px;}
.comp-body{font-size:13px;color:var(--muted);line-height:1.6;}
.tcpa-callout{background:var(--red-bg);border:1px solid var(--red-border);
  border-radius:13px;padding:14px 22px;margin-top:14px;
  display:flex;align-items:center;gap:18px;}
.tcpa-num{font-size:48px;font-weight:800;color:var(--red);flex-shrink:0;}
.tcpa-text{font-size:14px;color:#fca5a5;line-height:1.6;}

/* ── SLIDE 8 ── */
.calc-layout{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;}
.calc-inputs{display:flex;flex-direction:column;gap:9px;}
.calc-group{background:var(--card);border:1px solid var(--border);
  border-radius:12px;padding:13px 16px;}
.calc-label{font-size:12px;color:var(--muted);margin-bottom:5px;}
.calc-val{font-size:24px;font-weight:700;color:var(--blue-l);margin-bottom:3px;}
.calc-slider{width:100%;accent-color:var(--blue-l);margin-top:3px;}
.calc-results{display:flex;flex-direction:column;gap:8px;}
.result-card{border-radius:12px;padding:14px 16px;}
.result-num{font-size:30px;font-weight:800;margin-bottom:3px;}
.result-label{font-size:13px;color:var(--muted);}
.impact-reveal{background:linear-gradient(135deg,#0d2e1a,#0a2018);
  border:1.5px solid var(--green);border-radius:14px;padding:18px 24px;
  margin-top:14px;display:flex;justify-content:space-between;align-items:center;}
.impact-label{font-size:11px;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;color:#4ade80;margin-bottom:6px;}
.impact-big{font-size:52px;font-weight:800;color:var(--green);
  transition:all .3s ease;line-height:1;}
.impact-sub{font-size:13px;color:#4ade80;margin-top:4px;}
.impact-boxes{display:flex;gap:12px;}
.impact-box{text-align:center;min-width:90px;}
.ib-num{font-size:22px;font-weight:800;margin-bottom:2px;}
.ib-label{font-size:11px;color:#4ade80;opacity:.75;}
@keyframes pop{0%{transform:scale(1);}50%{transform:scale(1.1);}100%{transform:scale(1);}}
.popping{animation:pop .35s ease;}

/* ── SLIDE 9 ── */
.cpp-layout{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;}
.cpp-inputs{display:flex;flex-direction:column;gap:9px;}
.cpp-results{display:flex;flex-direction:column;gap:9px;}
.cpp-card{border-radius:13px;padding:16px 18px;}
.cpp-headline{font-size:32px;font-weight:800;margin-bottom:2px;}
.cpp-meaning{font-size:15px;font-weight:700;margin-bottom:4px;}
.cpp-sub{font-size:12px;color:var(--muted);line-height:1.5;}
.tier-toggle{display:flex;gap:8px;margin-top:6px;}
.tier-btn{flex:1;padding:9px;border-radius:8px;font-size:12px;font-weight:600;
  cursor:pointer;border:1px solid var(--border);background:var(--card);
  color:var(--muted);transition:all .15s;text-align:center;}
.tier-btn.selected{background:var(--blue-bg);border-color:var(--blue-l);
  color:var(--blue-l);}
.cpp-assumption{font-size:12px;color:var(--dim);margin-top:8px;
  padding:10px 14px;background:#0a0f1f;border-radius:9px;
  line-height:1.65;border:1px solid var(--border);}

/* ── SLIDE 10 ── */
.pkg-grid{display:grid;grid-template-columns:1fr 1fr;gap:11px;margin-top:14px;}
.pkg-item{display:flex;align-items:flex-start;gap:12px;background:var(--card);
  border-radius:13px;padding:15px 16px;border:1px solid var(--border);}
.pkg-icon{font-size:24px;min-width:32px;}
.pkg-title{font-size:15px;font-weight:700;margin-bottom:4px;}
.pkg-body{font-size:13px;color:var(--muted);line-height:1.55;}
.pkg-tools{font-size:11px;color:var(--dim);font-style:italic;margin-top:4px;}

/* ── SLIDE 11 ── */
.pricing-grid{display:grid;grid-template-columns:1fr 1.1fr 1fr;gap:13px;
  margin-top:14px;}
.price-card{background:var(--card);border:1px solid var(--border);
  border-radius:14px;padding:20px 18px;}
.price-card.featured{border-color:var(--blue-l);background:var(--blue-bg);}
.price-tier{font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:1px;color:var(--muted);margin-bottom:8px;}
.price-val{font-size:36px;font-weight:800;margin-bottom:2px;}
.price-per{font-size:13px;color:var(--muted);margin-bottom:14px;}
.price-feats{list-style:none;font-size:13px;color:var(--muted);line-height:2.2;}
.price-feats li::before{content:'✓ ';color:var(--green);}
.comp-table{width:100%;border-collapse:collapse;margin-top:13px;
  border-radius:11px;overflow:hidden;border:1px solid var(--border);}
.comp-table th{background:var(--surface);padding:9px 14px;font-size:11px;
  font-weight:700;text-transform:uppercase;letter-spacing:.7px;
  color:var(--muted);text-align:left;}
.comp-table td{padding:9px 14px;font-size:13px;border-top:1px solid var(--border);}
.comp-table .highlight-row td{background:#0d1a2e;font-weight:700;
  color:var(--blue-l);}

/* ── SLIDE 12 ── */
.onboard-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px;}
.onboard-step{background:var(--card);border:1px solid var(--border);
  border-radius:13px;padding:18px 18px;display:flex;gap:14px;align-items:flex-start;}
.onboard-num{width:40px;height:40px;border-radius:50%;background:var(--blue);
  display:flex;align-items:center;justify-content:center;
  font-weight:700;font-size:16px;flex-shrink:0;}
.onboard-title{font-size:16px;font-weight:700;margin-bottom:5px;}
.onboard-body{font-size:13px;color:var(--muted);line-height:1.6;}
.onboard-tools{font-size:11px;color:var(--dim);font-style:italic;margin-top:5px;}
.close-vision{background:var(--green-bg);border:1.5px solid var(--green-border);
  border-radius:14px;padding:20px 26px;margin-top:14px;
  display:flex;justify-content:space-between;align-items:center;}
.cv-text{font-size:16px;color:#4ade80;line-height:1.7;}
.cv-cta{text-align:right;}
.cv-cta-big{font-size:30px;font-weight:800;color:var(--green);}
.cv-cta-sub{font-size:14px;color:#4ade80;margin-top:3px;}
</style>
</head>
<body>

<div class="topbar">
  <div class="tb-left">
    <div class="tb-logo">🏥</div>
    <span class="tb-title">BlueLine Staffing AI</span>
    <span class="tb-sub">— Product Pitch</span>
  </div>
  <div class="tb-controls">
    <span class="slide-counter" id="slideCounter">1 / 12</span>
    <button class="ctrl-btn btn-ghost" id="notesBtn" onclick="toggleNotes()">📋 Speaker Notes</button>
    <button class="ctrl-btn btn-blue" id="narrationBtn" onclick="toggleNarration()">🔊 Narration On</button>
    <button class="ctrl-btn btn-blue" id="playBtn" onclick="toggleAutoPlay()">▶ Auto-Play</button>
  </div>
</div>
<div class="progress-bar"><div class="progress-fill" id="progressFill" style="width:8.33%"></div></div>

<div class="main-area">
<div class="slide-panel">
<div class="slide-viewport">

<!-- ═══ SLIDE 1 ═══ -->
<div class="slide active" id="slide-1">
  <div class="slide-tag">Introduction · 0:00 – 2:00</div>
  <h1>A Fully Automated AI Recruiting Agent<br>for Healthcare Staffing.</h1>
  <div class="deck-sub">Built for nursing homes and rehabilitation centers. Not a prototype — live, running daily, placing nurses now.</div>
  <div class="hero-tag-row">
    <span class="badge bdg-blue">NYC: All 5 Boroughs</span>
    <span class="badge bdg-green">Live · Running Daily</span>
    <span class="badge bdg-amber">TCPA Compliant</span>
    <span class="badge bdg-purple">Works with Your Existing SMS &amp; Email Stack</span>
    <span class="badge" style="background:#1a1008;color:#f59e0b;">White-Label Ready</span>
  </div>
  <div class="hero-metrics">
    <div class="hero-metric">
      <div class="stat blue">344+</div>
      <div class="stat-label">Candidates contacted to date</div>
    </div>
    <div class="hero-metric">
      <div class="stat green">41</div>
      <div class="stat-label">Active conversations this week</div>
    </div>
    <div class="hero-metric">
      <div class="stat amber">30</div>
      <div class="stat-label">New leads contacted every morning</div>
    </div>
    <div class="hero-metric">
      <div class="stat" style="color:#c4b5fd;">4,421</div>
      <div class="stat-label">Contacts tracked in live system</div>
    </div>
  </div>
  <table class="response-table">
    <thead><tr>
      <th>Action</th>
      <th>Human recruiter</th>
      <th>BlueLine AI</th>
      <th>Source</th>
    </tr></thead>
    <tbody>
      <tr>
        <td>Reply when a nurse texts YES</td>
        <td class="td-bad">4.2 hrs avg</td>
        <td class="td-good">&lt; 10 seconds</td>
        <td class="td-src">InsideSales Lead Response Report 2024</td>
      </tr>
      <tr>
        <td>First outreach to a new lead</td>
        <td class="td-bad">2–4 hrs (manual prep)</td>
        <td class="td-good">8:00 AM, daily, automatic</td>
        <td class="td-src">Internal benchmark</td>
      </tr>
      <tr>
        <td>Document checklist after submission</td>
        <td class="td-bad">15–45 min</td>
        <td class="td-good">Instant, triggered on email receipt</td>
        <td class="td-src">ASHHRA 2022 Workforce Survey</td>
      </tr>
      <tr>
        <td>Follow-up to silent candidate</td>
        <td class="td-bad">1–3 days (if remembered)</td>
        <td class="td-good">96 hrs exactly — automated</td>
        <td class="td-src">Internal SLA</td>
      </tr>
      <tr>
        <td>Opt-out handling (STOP reply)</td>
        <td class="td-bad">Manual — days of exposure risk</td>
        <td class="td-good">Instant permanent block</td>
        <td class="td-src">47 U.S.C. § 227 (TCPA)</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- ═══ SLIDE 2 ═══ -->
<div class="slide" id="slide-2">
  <div class="slide-tag">The Problem · 2:00 – 5:00</div>
  <h2>Your Recruiter's Morning. Every Morning. For Every Lead.</h2>
  <div class="deck-sub">Before a single nurse is placed, your team burns hours on work that's fully automatable. Here's the real cost of that.</div>
  <div class="pain-grid">
    <div class="pain-item">
      <div class="pain-icon">⏰</div>
      <div class="pain-title">750+ Hours a Year — Texting Nurses One by One, Copy-Paste by Copy-Paste</div>
      <div class="pain-body">2–3 hours every morning. Same message. Different number. No way to scale without hiring another person and spending another $62,000. That's 18+ weeks of a full-time salary spent doing what a script can do in 4 minutes.</div>
    </div>
    <div class="pain-item">
      <div class="pain-icon">📉</div>
      <div class="pain-title">40% of Candidates Who Say Yes Never Make It to a Shift</div>
      <div class="pain-body">Average agency response time: 4+ hours. Average nurse response window after an SMS: 90 seconds. By the time your recruiter replies, she's accepted a shift at a competing agency. Speed is the placement. <span style="font-size:11px;opacity:.6;">(Source: CTIA 2023, InsideSales.com)</span></div>
    </div>
    <div class="pain-item" style="border-color:#dc2626;background:#200a0a;">
      <div class="pain-icon">⚖️</div>
      <div class="pain-title" style="color:#ff6b6b;font-size:18px;">$1,500 Fine Per Missed Opt-Out — Per Text, Per Violation</div>
      <div class="pain-body">Federal TCPA fine per unsolicited message to an opted-out number. One CSV re-import that overwrites your stop list exposes you to hundreds of those. Per message. Not per campaign. <span style="font-size:11px;opacity:.6;">(Source: 47 U.S.C. § 227)</span></div>
    </div>
    <div class="pain-item">
      <div class="pain-icon">📄</div>
      <div class="pain-title">45–90 Minutes Per Credential Review — For Every Candidate</div>
      <div class="pain-body">Eight document types. NYS date windows. License expiry. Physical recency. Titers. TB. BLS. I-9. Manual review, every candidate, every time. Before you can submit a single person to a facility.</div>
    </div>
  </div>
  <div class="vs-bar">
    <div class="vs-side">
      <div class="vs-label" style="color:var(--red);">Manual response time</div>
      <div class="vs-val" style="color:var(--red);">4+ hours</div>
      <div style="font-size:12px;color:var(--muted);margin-top:4px;">Candidate waits, loses interest, takes another shift</div>
    </div>
    <div class="vs-arrow">→</div>
    <div class="vs-side">
      <div class="vs-label" style="color:var(--green);">BlueLine response time</div>
      <div class="vs-val" style="color:var(--green);">&lt; 10 seconds</div>
      <div style="font-size:12px;color:var(--muted);margin-top:4px;">Document checklist sent before recruiter opens laptop</div>
    </div>
    <div class="vs-arrow">→</div>
    <div class="vs-side">
      <div class="vs-label" style="color:var(--amber);">Net impact</div>
      <div class="vs-val" style="color:var(--amber);">40% more placements</div>
      <div style="font-size:12px;color:var(--muted);margin-top:4px;">From response speed alone — before any other gain</div>
    </div>
  </div>
</div>

<!-- ═══ SLIDE 3 ═══ -->
<div class="slide" id="slide-3">
  <div class="slide-tag">The Full Process · 5:00 – 9:00</div>
  <h2>The Healthcare Recruitment Journey — 6 Stages, 12–20 Hours, 36–49 Days</h2>
  <div class="deck-sub">This is the end-to-end cost of one placed nurse. BlueLine compresses the first four stages to zero and automates 83% of stage five.</div>
  <div class="journey-flow">
    <div class="j-stage">
      <div class="j-num">1</div>
      <div class="j-title">Lead Discovery</div>
      <div class="j-manual">Manual: 5–15 min</div>
      <div class="j-ai">AI: 0 min ✓</div>
      <div class="j-tags">
        <span class="j-tag">Indeed</span><span class="j-tag">LinkedIn</span>
        <span class="j-tag">ZipRecruiter</span><span class="j-tag">Vivian</span>
        <span class="j-tag">NurseRecruiter</span><span class="j-tag">CSV</span>
      </div>
    </div>
    <div class="j-stage">
      <div class="j-num">2</div>
      <div class="j-title">Info Assimilation</div>
      <div class="j-manual">Manual: 10–20 min</div>
      <div class="j-ai">AI: 0 min ✓</div>
      <div class="j-tags">
        <span class="j-tag">License type</span><span class="j-tag">Specialty</span>
        <span class="j-tag">Location</span><span class="j-tag">Availability</span>
      </div>
    </div>
    <div class="j-stage">
      <div class="j-num">3</div>
      <div class="j-title">Portal / ATS Entry</div>
      <div class="j-manual">Manual: 15–30 min</div>
      <div class="j-ai">AI: 0 min ✓</div>
      <div class="j-tags">
        <span class="j-tag">Bullhorn</span><span class="j-tag">TempWorks</span>
        <span class="j-tag">Avionte</span><span class="j-tag">Spreadsheet</span>
      </div>
    </div>
    <div class="j-stage">
      <div class="j-num">4</div>
      <div class="j-title">Candidate Comms</div>
      <div class="j-manual">Manual: 2–4 hrs</div>
      <div class="j-ai">AI: 0 min ✓</div>
      <div class="j-tags">
        <span class="j-tag">5–7 touches avg</span>
        <span class="j-tag">SMS</span><span class="j-tag">Email</span>
        <span class="j-tag">2–3 weeks</span>
      </div>
    </div>
    <div class="j-stage">
      <div class="j-num">5</div>
      <div class="j-title">Document Review</div>
      <div class="j-manual">Manual: 45–90 min</div>
      <div class="j-ai">AI: 10–15 min ✓</div>
      <div class="j-tags">
        <span class="j-tag">License</span><span class="j-tag">Physical</span>
        <span class="j-tag">Titers</span><span class="j-tag">TB</span>
        <span class="j-tag">BLS</span><span class="j-tag">I-9</span>
      </div>
    </div>
    <div class="j-stage">
      <div class="j-num">6</div>
      <div class="j-title">Credential &amp; Submit</div>
      <div class="j-manual">Manual: 2–4 hrs</div>
      <div class="j-ai">AI: ~90 min ✓</div>
      <div class="j-tags">
        <span class="j-tag">Background</span><span class="j-tag">References</span>
        <span class="j-tag">Application</span><span class="j-tag">Submission</span>
      </div>
    </div>
  </div>
  <div class="journey-table">
    <div class="jt-row jt-hdr">
      <div class="jt-cell">Stage</div>
      <div class="jt-cell">Manual time</div>
      <div class="jt-cell">With BlueLine</div>
      <div class="jt-cell">Reduction</div>
    </div>
    <div class="jt-row">
      <div class="jt-cell">Stages 1–4 · Discovery → Comms</div>
      <div class="jt-cell" style="color:var(--red);font-weight:700;">3–5 hrs</div>
      <div class="jt-cell" style="color:var(--green);font-weight:700;">0 min</div>
      <div class="jt-cell" style="color:var(--green);font-weight:800;">−100%</div>
    </div>
    <div class="jt-row">
      <div class="jt-cell">Stage 5 · Document review</div>
      <div class="jt-cell" style="color:var(--red);font-weight:700;">45–90 min</div>
      <div class="jt-cell" style="color:var(--green);font-weight:700;">10–15 min</div>
      <div class="jt-cell" style="color:var(--green);font-weight:800;">−83%</div>
    </div>
    <div class="jt-row">
      <div class="jt-cell">Stage 6 · Credentialing + submit</div>
      <div class="jt-cell" style="color:var(--red);font-weight:700;">2–4 hrs</div>
      <div class="jt-cell" style="color:var(--amber);font-weight:700;">~90 min</div>
      <div class="jt-cell" style="color:var(--amber);font-weight:800;">−60%</div>
    </div>
    <div class="jt-row">
      <div class="jt-cell">Total per placed nurse · time-to-fill</div>
      <div class="jt-cell" style="color:var(--red);font-weight:700;">12–20 hrs · 36–49 days</div>
      <div class="jt-cell" style="color:var(--green);font-weight:700;">~2 hrs · 25–32 days</div>
      <div class="jt-cell" style="color:var(--green);font-weight:800;">~85% less</div>
    </div>
  </div>
  <div class="src">Sources: ASHHRA 2022 Annual Workforce Survey (49-day RN time-to-fill) · SHRM Talent Acquisition Benchmark 2023 (outreach time) · InsideSales/MIT HBR (5–7 follow-up touches) · NYS DOH credential requirements (document scope)</div>
</div>

<!-- ═══ SLIDE 4 ═══ -->
<div class="slide" id="slide-4">
  <div class="slide-tag">Financial Case · 9:00 – 13:00</div>
  <h2>The Real Cost of Doing This Manually</h2>
  <div class="deck-sub">The advertised recruiter salary is never the actual cost. Here's what one recruiter running this pipeline costs your agency per year — and what's hidden underneath it.</div>
  <table class="cost-table">
    <thead><tr><th>Cost Component</th><th>Annual Cost</th><th>Source</th></tr></thead>
    <tbody>
      <tr><td>Base salary</td><td class="td-red">$45,000</td><td class="td-note">BLS OES 2023 — HR Specialists, entry-level healthcare staffing</td></tr>
      <tr><td>Employer payroll taxes (FICA + FUTA)</td><td class="td-red">$3,900</td><td class="td-note">~8.65% of base</td></tr>
      <tr><td>Health insurance (employer share)</td><td class="td-red">$7,000</td><td class="td-note">KFF 2023 Employer Health Benefits Survey: avg $7,034/yr</td></tr>
      <tr><td>Tools: ATS, SMS platform, job boards</td><td class="td-red">$4,800</td><td class="td-note">Bullhorn/TempWorks + Indeed + SMS platform est.</td></tr>
      <tr><td>Onboarding, training, overhead</td><td class="td-red">$1,940</td><td class="td-note">SHRM: $4,100 avg onboarding, amortized over 2yr tenure</td></tr>
      <tr class="total-row"><td>Total annual cost — one recruiter</td><td class="td-red">$62,640</td><td class="td-note"></td></tr>
    </tbody>
  </table>
  <div class="savings-banner">
    <div>
      <div class="savings-num">$44,640 saved</div>
      <div class="savings-label">Direct annual savings — BlueLine Professional vs. one human recruiter</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:15px;color:#4ade80;font-weight:700;">BlueLine Professional: $18,000/yr</div>
      <div style="font-size:13px;color:var(--muted);margin-top:3px;">Outreach · Re-engagement · Document review · TCPA · Reporting</div>
    </div>
  </div>

  <div class="downtime-header">⏸ The number that's never in the proposal: Recruiter downtime</div>
  <div class="downtime-grid">
    <div class="dg-hdr">
      <div class="dg-cell">Absence type</div>
      <div class="dg-cell">Days/yr</div>
      <div class="dg-cell">% of year</div>
      <div class="dg-cell">Source</div>
    </div>
    <div><div class="dg-cell">Sick days used</div><div class="dg-cell" style="color:var(--amber);">7.7</div><div class="dg-cell" style="color:var(--muted);">3.0%</div><div class="dg-cell" style="color:var(--muted);">BLS National Compensation Survey 2023</div></div>
    <div><div class="dg-cell">Vacation days (1–5yr tenure)</div><div class="dg-cell" style="color:var(--amber);">12</div><div class="dg-cell" style="color:var(--muted);">4.6%</div><div class="dg-cell" style="color:var(--muted);">BLS Employee Benefits Survey 2023</div></div>
    <div><div class="dg-cell">Unscheduled absences (personal, no-shows)</div><div class="dg-cell" style="color:var(--amber);">7.3</div><div class="dg-cell" style="color:var(--muted);">2.8%</div><div class="dg-cell" style="color:var(--muted);">SHRM Absence Management Survey 2023</div></div>
    <div><div class="dg-cell">Paid federal holidays</div><div class="dg-cell" style="color:var(--amber);">10</div><div class="dg-cell" style="color:var(--muted);">3.8%</div><div class="dg-cell" style="color:var(--muted);">OPM standard / common private employer match</div></div>
    <div class="dg-total"><div class="dg-cell">Total unproductive days per year</div><div class="dg-cell" style="color:var(--red);font-size:16px;">37</div><div class="dg-cell" style="color:var(--red);">14.2%</div><div class="dg-cell" style="color:var(--green);">BlueLine: 0 days · Runs 365 days/yr</div></div>
  </div>
  <div class="downtime-impact">
    <div class="dt-card"><div class="dt-num">$8,910</div><div class="dt-label">Salary paid for 37 zero-output days (fully loaded)</div></div>
    <div class="dt-card"><div class="dt-num">1,110</div><div class="dt-label">Candidates never contacted (37 days × 30 leads/day)</div></div>
    <div class="dt-card"><div class="dt-num">~$99,000</div><div class="dt-label">Missed gross margin — ~55 lost placements at $1,800 avg</div></div>
  </div>
  <div class="true-cost-banner">
    <div class="tc-left">
      Direct compensation + overhead &nbsp;→&nbsp; $62,640<br>
      Paid unproductive time &nbsp;→&nbsp; $8,910<br>
      Missed placement revenue (conservative, 5% rate) &nbsp;→&nbsp; ~$99,000
    </div>
    <div style="text-align:right;">
      <div class="tc-num">~$161,640/yr</div>
      <div style="font-size:14px;color:var(--muted);">True annual cost of one human recruiter</div>
      <div class="tc-vs">vs. BlueLine: $18,000/yr · 365 days · 0 absences</div>
    </div>
  </div>
</div>

<!-- ═══ SLIDE 5 ═══ -->
<div class="slide" id="slide-5">
  <div class="slide-tag">Product · 13:00 – 17:00</div>
  <h2>Four Steps. Every Morning. No Human Trigger Required.</h2>
  <div class="deck-sub">The agent runs in a fixed execution order designed around candidate urgency — inbound first, stalled second, fresh outreach last.</div>
  <div class="steps-grid">
    <div class="step-card s1">
      <div class="step-num" style="color:var(--green);">STEP 1</div>
      <div class="step-name" style="color:#4ade80;">New Lead Intro</div>
      <div class="step-body">30 new candidates contacted every morning — 150 on catch-up weeks. Borough and license-aware from the first message. Every contact deduped against all live records before sending. Marked processed only on confirmed delivery.</div>
      <div class="step-rationale" style="color:#4ade80;">↓ Top of the funnel — pipeline grows daily</div>
      <div class="step-tools"><strong>Lead sources:</strong> Indeed CSV, LinkedIn export, Vivian Health, ZipRecruiter, internal spreadsheet</div>
    </div>
    <div class="step-card s2">
      <div class="step-num" style="color:var(--blue-l);">STEP 2</div>
      <div class="step-name" style="color:#93c5fd;">SMS Reply Handler</div>
      <div class="step-body">Scans all inbound SMS. YES → document checklist sent in &lt;10 seconds. STOP → permanent block and contact rename, instantly. Unclear → human review queue with full conversation context attached.</div>
      <div class="step-rationale" style="color:#93c5fd;">↓ Candidates responded — close the loop fast</div>
      <div class="step-tools"><strong>Works with:</strong> OpenPhone, Podium, Twilio, EZTexting, TextMagic, SimpleTexting, Salesmsg</div>
    </div>
    <div class="step-card s3">
      <div class="step-num" style="color:var(--amber);">STEP 3</div>
      <div class="step-name" style="color:#fcd34d;">Re-engage Stalled</div>
      <div class="step-body">Contacts silent 96+ hrs get a personalised follow-up — but only after the AI reads 4 days of SMS and email history. If they're mid-process, it skips entirely. Never sends a redundant or generic message.</div>
      <div class="step-rationale" style="color:#fcd34d;">↓ No reply? Recover before they go cold</div>
      <div class="step-tools"><strong>Works with:</strong> Same SMS platform as Step 2 + Gmail/Outlook for email context</div>
    </div>
    <div class="step-card s4">
      <div class="step-num" style="color:var(--purple);">STEP 4</div>
      <div class="step-name" style="color:#c4b5fd;">Document Review</div>
      <div class="step-body">AI Vision reads every inbound credential attachment — license, physical, titers, TB, BLS, I-9. Validates all NYS date windows. Drafts a ✓/✗ checklist reply. Waiting in your inbox before 8 AM, same day as submission.</div>
      <div class="step-rationale" style="color:#c4b5fd;">↓ Serious candidate — get them credentialed fast</div>
      <div class="step-tools"><strong>Works with:</strong> Gmail, Microsoft Outlook, Apple Mail — any inbox that receives attachments</div>
    </div>
  </div>
  <div class="three-col" style="margin-top:12px;">
    <div class="card card-green">
      <div class="stat green" style="font-size:32px;">344+</div>
      <div class="stat-label">Total leads processed to date</div>
    </div>
    <div class="card card-blue">
      <div class="stat blue" style="font-size:32px;">4,421</div>
      <div class="stat-label">Live contacts — deduplicated</div>
    </div>
    <div class="card card-purple">
      <div class="stat purple" style="font-size:32px;">41</div>
      <div class="stat-label">Active conversations this week</div>
    </div>
  </div>
</div>

<!-- ═══ SLIDE 6 ═══ -->
<div class="slide" id="slide-6">
  <div class="slide-tag">Differentiator · 17:00 – 20:00</div>
  <h2>The Intelligence That Sets BlueLine Apart From Every Competitor</h2>
  <div class="deck-sub">Every other platform fires the same blast to every number and waits. BlueLine reads 4 days of SMS history and email threads — then decides what to send, or whether to send at all.</div>
  <div class="examples-grid">
    <div class="ex-pair">
      <div class="ex-label" style="color:var(--red);">❌ Standard Automation</div>
      <div class="bubble bad">"Hi Maria, are you still interested in CNA shifts? We have openings in NYC. Reply YES to connect."<br><br><em style="font-size:12px;opacity:.6;">— Sent 2 days after Maria submitted all her documents.</em></div>
      <div class="ex-result loss">Maria feels ignored. She moves to another agency.</div>
      <div style="height:10px;"></div>
      <div class="bubble bad">"Hi James, we have great opportunities available! Are you interested in picking up shifts this week?"<br><br><em style="font-size:12px;opacity:.6;">— Sent while James is waiting to hear back after his YES reply 3 days ago.</em></div>
      <div class="ex-result loss">James thinks his YES was missed. He stops responding.</div>
    </div>
    <div class="ex-pair">
      <div class="ex-label" style="color:var(--green);">✓ BlueLine Context-Aware</div>
      <div class="bubble good">"Hi Maria, just checking in — you sent your documents over on Monday. Our team is reviewing and will be in touch by Thursday. Anything else you need from us?"<br><br><em style="font-size:12px;opacity:.6;">— BlueLine read the email thread. Saw she submitted. Sent reassurance.</em></div>
      <div class="ex-result win">Maria feels seen. She stays engaged. Candidate retained.</div>
      <div style="height:10px;"></div>
      <div class="bubble good">"Hi James — still pulling together your schedule options. Are Brooklyn or Bronx facilities closer for you? Trying to get you something nearby."<br><br><em style="font-size:12px;opacity:.6;">— BlueLine read his YES, saw no follow-through, sent a relevant next step.</em></div>
      <div class="ex-result win">James re-engages. Placement moves forward.</div>
    </div>
  </div>
  <div class="context-engine">
    <div style="font-size:14px;font-weight:700;margin-bottom:10px;">How the Context Engine Works — Every Single Time</div>
    <div class="ce-steps">
      <div class="ce-step"><span style="color:var(--blue-l);font-weight:700;">① Pull SMS history</span><br>Last 4 days of text conversation for this exact number from your SMS platform.</div>
      <div class="ce-step"><span style="color:var(--blue-l);font-weight:700;">② Pull email threads</span><br>Searches candidate's name across your email for the last 4 days. Reads subject + body.</div>
      <div class="ce-step"><span style="color:var(--blue-l);font-weight:700;">③ Claude AI decides</span><br>Returns SKIP (mid-process, don't disturb) or a personalised SMS referencing real context.</div>
    </div>
  </div>
</div>

<!-- ═══ SLIDE 7 ═══ -->
<div class="slide" id="slide-7">
  <div class="slide-tag">Compliance · 20:00 – 22:00</div>
  <h2>Built for Healthcare. Every Safeguard, by Design.</h2>
  <div class="deck-sub">Healthcare staffing carries one of the highest TCPA liability profiles of any industry. Every compliance layer was built before we built the outreach engine.</div>
  <div class="comp-grid">
    <div class="comp-card">
      <div class="comp-icon">🛑</div>
      <div class="comp-title">Permanent Opt-Out Registry</div>
      <div class="comp-body">Any STOP or UNSUBSCRIBE is written to a permanent file that survives system restarts, re-imports, and CSV re-loads. That number is never contacted again — ever. No workflow, no import, no API call can override it.</div>
    </div>
    <div class="comp-card">
      <div class="comp-icon">✋</div>
      <div class="comp-title">Human-in-the-Loop Email — Always</div>
      <div class="comp-body">Every document reply — credential feedback, checklist, application form — is saved as a draft in your email system. A human reviews it and sends it. Nothing reaches a candidate's inbox automatically. Ever.</div>
    </div>
    <div class="comp-card">
      <div class="comp-icon">📋</div>
      <div class="comp-title">NYS License &amp; Document Validation</div>
      <div class="comp-body">Flags expired licenses, out-of-state credentials, TB tests older than 9 months, physicals older than 12 months, and titers older than 5 years — before your team wastes time on an unsubmittable candidate.</div>
    </div>
    <div class="comp-card">
      <div class="comp-icon">🔒</div>
      <div class="comp-title">Full Timestamped Audit Trail</div>
      <div class="comp-body">Every SMS sent, skipped, or flagged is written to a per-run CSV log with timestamp, candidate name, phone, and decision reason. Fully defensible in a TCPA audit. Ready on demand.</div>
    </div>
    <div class="comp-card">
      <div class="comp-icon">📋</div>
      <div class="comp-title">I-9 Compliance Verification</div>
      <div class="comp-body">AI validates the correct combination of identity documents — List A alone, or List B + List C. Flags incomplete or invalid I-9 configurations before the candidate enters your submission pipeline.</div>
    </div>
    <div class="comp-card">
      <div class="comp-icon">🔍</div>
      <div class="comp-title">Hardcoded Blocked Numbers</div>
      <div class="comp-body">Specific numbers can be permanently blocked at the system level — independent of the opt-out file. Cannot be overridden by any CSV import, API call, or manual action. Structural protection.</div>
    </div>
  </div>
  <div class="tcpa-callout">
    <div class="tcpa-num">$1,500</div>
    <div class="tcpa-text">Maximum TCPA fine per unsolicited text to an opted-out number. (47 U.S.C. § 227)<br><strong style="color:#fca5a5;">BlueLine's permanent opt-out architecture makes accidental re-contact structurally impossible — not by policy, by code.</strong></div>
  </div>
</div>

<!-- ═══ SLIDE 8 ═══ -->
<div class="slide" id="slide-8">
  <div class="slide-tag">ROI · 22:00 – 24:30</div>
  <h2>Your Numbers — Live ROI Calculator</h2>
  <div class="deck-sub">Dial in your agency's actual figures. The return updates in real time.</div>
  <div class="calc-layout">
    <div class="calc-inputs">
      <div class="calc-group">
        <div class="calc-label">Nurses placed per month (current)</div>
        <div class="calc-val" id="cPlaced">8</div>
        <input type="range" class="calc-slider" id="sliderPlaced" min="2" max="30" value="8" oninput="calcROI()">
      </div>
      <div class="calc-group">
        <div class="calc-label">Average hourly bill rate to facility ($)</div>
        <div class="calc-val" id="cBill">$38</div>
        <input type="range" class="calc-slider" id="sliderBill" min="20" max="75" value="38" oninput="calcROI()">
      </div>
      <div class="calc-group">
        <div class="calc-label">Agency margin per billable hour (%)</div>
        <div class="calc-val" id="cMargin">35%</div>
        <input type="range" class="calc-slider" id="sliderMargin" min="15" max="55" value="35" oninput="calcROI()">
      </div>
      <div class="calc-group">
        <div class="calc-label">Average shifts per placed nurse / week</div>
        <div class="calc-val" id="cShifts">3</div>
        <input type="range" class="calc-slider" id="sliderShifts" min="1" max="5" value="3" oninput="calcROI()">
      </div>
    </div>
    <div class="calc-results">
      <div class="result-card card-green">
        <div class="result-num" style="color:var(--green);font-size:22px;" id="rGainPlacements">—</div>
        <div class="result-label" style="font-weight:700;">① Revenue from +25% placement lift</div>
        <div style="font-size:12px;color:var(--muted);margin-top:3px;">Conservative — most agencies see this in 60 days from faster response alone</div>
      </div>
      <div class="result-card card-amber">
        <div class="result-num" style="color:var(--amber);font-size:22px;" id="rGainDowntime">—</div>
        <div class="result-label" style="font-weight:700;">② Downtime coverage value</div>
        <div style="font-size:12px;color:var(--muted);margin-top:3px;">37 days × 30 leads × 5% placement rate — nurses contacted on days a human wouldn't be in</div>
      </div>
      <div class="result-card card-blue">
        <div class="result-num" style="color:var(--blue-l);font-size:22px;" id="rGainTime">~$22K</div>
        <div class="result-label" style="font-weight:700;">③ Recruiter time freed</div>
        <div style="font-size:12px;color:var(--muted);margin-top:3px;">750 hrs/yr of copy-paste outreach eliminated → redirected to placements, credentialing, client relationships</div>
      </div>
      <div class="result-card card-purple">
        <div class="result-num" style="color:var(--purple);font-size:22px;" id="rPayback">—</div>
        <div class="result-label" style="font-weight:700;">Subscription payback period</div>
        <div style="font-size:12px;color:var(--muted);margin-top:3px;">BlueLine Professional at $1,500/mo</div>
      </div>
    </div>
  </div>
  <div class="impact-reveal">
    <div>
      <div class="impact-label">Three Streams of Value — Total Year-One Advantage</div>
      <div class="impact-big" id="impactBig">—</div>
      <div class="impact-sub">All three benefit streams combined, minus BlueLine annual cost</div>
    </div>
    <div class="impact-boxes">
      <div class="impact-box">
        <div class="ib-num" style="color:var(--green);" id="ibPlacement">—</div>
        <div class="ib-label">① Placement lift</div>
      </div>
      <div class="impact-box">
        <div class="ib-num" style="color:var(--amber);" id="ibDowntime">—</div>
        <div class="ib-label">② Downtime</div>
      </div>
      <div class="impact-box">
        <div class="ib-num" style="color:var(--blue-l);">+$22K</div>
        <div class="ib-label">③ Time freed</div>
      </div>
      <div class="impact-box">
        <div class="ib-num" style="color:#fca5a5;">−$18K</div>
        <div class="ib-label">BlueLine cost</div>
      </div>
    </div>
  </div>
</div>

<!-- ═══ SLIDE 9 ═══ -->
<div class="slide" id="slide-9">
  <div class="slide-tag">Unit Economics · 24:30 – 26:30</div>
  <h2>Cost Per Placement — Manual vs. AI-Assisted</h2>
  <div class="deck-sub">The real question isn't what BlueLine costs. It's what each placement costs you — and how much that drops when outreach is fully automated.</div>
  <div class="cpp-layout">
    <div class="cpp-inputs">
      <div class="calc-group">
        <div class="calc-label">Number of recruiters doing outreach</div>
        <div class="calc-val" id="cpRC">1</div>
        <input type="range" class="calc-slider" id="slRC" min="1" max="8" value="1" oninput="calcCPP()">
      </div>
      <div class="calc-group">
        <div class="calc-label">Annual cost per recruiter (salary + full overhead)</div>
        <div class="calc-val" id="cpCost">$62K</div>
        <input type="range" class="calc-slider" id="slCost" min="45000" max="110000" step="1000" value="62000" oninput="calcCPP()">
      </div>
      <div class="calc-group">
        <div class="calc-label">Current placements per recruiter per month</div>
        <div class="calc-val" id="cpPl">8</div>
        <input type="range" class="calc-slider" id="slPl" min="2" max="25" value="8" oninput="calcCPP()">
      </div>
      <div class="calc-group">
        <div class="calc-label">Choose your BlueLine plan</div>
        <div class="tier-toggle">
          <div class="tier-btn selected" id="tS" onclick="selTier('starter')">Starter · $800/mo</div>
          <div class="tier-btn" id="tP" onclick="selTier('pro')">Professional · $1,500/mo</div>
        </div>
      </div>
      <div class="cpp-assumption">Assumption: BlueLine automates stages 1–4 (outreach, follow-up, ATS entry, reply handling), freeing ~45% of recruiter time. Conservative +25% placement rate from faster response alone. Source: HCI Candidate Conversion Studies 2023.</div>
    </div>
    <div class="cpp-results">
      <div class="cpp-card card-red">
        <div class="cpp-headline" style="color:var(--red);" id="rManualCPP">—</div>
        <div class="cpp-meaning" style="color:#fca5a5;">What You Pay Per Placement Today</div>
        <div class="cpp-sub">Recruiter annual cost ÷ total monthly placements</div>
      </div>
      <div class="cpp-card card-green">
        <div class="cpp-headline" style="color:var(--green);" id="rAICPP">—</div>
        <div class="cpp-meaning" style="color:#4ade80;">Cost Per Placement With BlueLine</div>
        <div class="cpp-sub">Same recruiter, 45% more placements handled</div>
      </div>
      <div class="cpp-card card-amber">
        <div class="cpp-headline" style="color:var(--amber);" id="rExtra">—</div>
        <div class="cpp-meaning" style="color:#fcd34d;">Extra Placements Monthly — Same Headcount</div>
        <div class="cpp-sub">From time reclaimed in stages 1–4 alone</div>
      </div>
      <div class="cpp-card card-purple">
        <div class="cpp-headline" style="color:var(--purple);" id="rSaving">—</div>
        <div class="cpp-meaning" style="color:#c4b5fd;">Annual Cost Reduction Per Recruiter</div>
        <div class="cpp-sub">Vs. fully manual process — includes BlueLine fee</div>
      </div>
    </div>
  </div>
</div>

<!-- ═══ SLIDE 10 ═══ -->
<div class="slide" id="slide-10">
  <div class="slide-tag">Scope · 26:30 – 28:00</div>
  <h2>Everything Included. No Add-Ons. No Surprises.</h2>
  <div class="deck-sub">One subscription covers the full pipeline. No modules, no per-seat licensing, no implementation project.</div>
  <div class="pkg-grid">
    <div class="pkg-item">
      <div class="pkg-icon">💬</div>
      <div>
        <div class="pkg-title">Automated SMS Outreach</div>
        <div class="pkg-body">30 new candidates/day — 150 on catch-up. License-aware, borough-aware, your recruiter persona from the first message.</div>
        <div class="pkg-tools">SMS platform: OpenPhone, Podium, Twilio, EZTexting, TextMagic, Salesmsg</div>
      </div>
    </div>
    <div class="pkg-item">
      <div class="pkg-icon">🧠</div>
      <div>
        <div class="pkg-title">Context-Aware Re-engagement</div>
        <div class="pkg-body">Reads every SMS thread and email history before any follow-up. Never sends a generic blast. Skips anyone mid-process automatically.</div>
        <div class="pkg-tools">Reads from: your SMS platform + Gmail / Outlook</div>
      </div>
    </div>
    <div class="pkg-item">
      <div class="pkg-icon">📋</div>
      <div>
        <div class="pkg-title">Document Intelligence (AI Vision)</div>
        <div class="pkg-body">Reads PDFs and photos. Validates 8 credential types against NYS date windows. Drafts a personalised reply — before your team opens their email.</div>
        <div class="pkg-tools">Email: Gmail, Microsoft Outlook, Apple Mail — any IMAP-compatible inbox</div>
      </div>
    </div>
    <div class="pkg-item">
      <div class="pkg-icon">🔄</div>
      <div>
        <div class="pkg-title">Instant SMS Reply Classification</div>
        <div class="pkg-body">YES → document checklist in under 10 seconds. STOP → permanent block. Unclear → human review queue with full conversation context included.</div>
        <div class="pkg-tools">Works via: any connected SMS platform</div>
      </div>
    </div>
    <div class="pkg-item">
      <div class="pkg-icon">🛡️</div>
      <div>
        <div class="pkg-title">TCPA Compliance Architecture</div>
        <div class="pkg-body">Permanent opt-out file. Hardcoded blocked number registry. Human-in-loop for all outbound email. Full timestamped audit log — TCPA-defensible on demand.</div>
        <div class="pkg-tools">Log output: CSV to shared drive, S3, or local storage</div>
      </div>
    </div>
    <div class="pkg-item">
      <div class="pkg-icon">📊</div>
      <div>
        <div class="pkg-title">Daily Run Reports</div>
        <div class="pkg-body">Every action logged per run: sent, skipped, flagged, blocked — with candidate name, phone, and the reason for each decision. Full audit trail.</div>
        <div class="pkg-tools">Delivery: CSV · email digest · shared folder</div>
      </div>
    </div>
    <div class="pkg-item">
      <div class="pkg-icon">🗺️</div>
      <div>
        <div class="pkg-title">Borough-Aware Routing</div>
        <div class="pkg-body">Auto-detects candidate borough from address and ZIP. Stored in contact record — drives personalisation, reporting, and routing at every step automatically.</div>
        <div class="pkg-tools">Contact storage: SMS platform CRM · ATS export · CSV</div>
      </div>
    </div>
    <div class="pkg-item">
      <div class="pkg-icon">⚙️</div>
      <div>
        <div class="pkg-title">Fully White-Labelled</div>
        <div class="pkg-body">Your recruiter persona. Your agency number. Your pay rates and facility list. Your message templates. Candidates interact with your brand — never BlueLine's.</div>
        <div class="pkg-tools">Identity: your agency name · your existing number · your voice</div>
      </div>
    </div>
  </div>
</div>

<!-- ═══ SLIDE 11 ═══ -->
<div class="slide" id="slide-11">
  <div class="slide-tag">Pricing · 28:00 – 29:00</div>
  <h2>Simple, Transparent Pricing — Validated Against the Market</h2>
  <div class="deck-sub">No per-seat licensing. No usage caps. No surprise module fees.</div>
  <div class="pricing-grid">
    <div class="price-card">
      <div class="price-tier">Starter</div>
      <div class="price-val">$800<span style="font-size:16px;font-weight:400;">/mo</span></div>
      <div class="price-per">Setup fee: $1,500 one-time</div>
      <ul class="price-feats">
        <li>CSV lead outreach (30/day)</li>
        <li>SMS reply classification</li>
        <li>Basic re-engagement</li>
        <li>Permanent TCPA opt-out system</li>
        <li>Daily run log CSV</li>
        <li>Email: draft-only</li>
      </ul>
    </div>
    <div class="price-card featured">
      <div style="margin-bottom:8px;"><span class="badge bdg-blue">Most Popular — 90% of agencies</span></div>
      <div class="price-tier" style="color:var(--blue-l);">Professional</div>
      <div class="price-val">$1,500<span style="font-size:16px;font-weight:400;">/mo</span></div>
      <div class="price-per">Setup fee: $2,000 one-time · = $50/day</div>
      <ul class="price-feats">
        <li>Everything in Starter</li>
        <li>Context-aware AI re-engagement</li>
        <li>Document review (Vision AI)</li>
        <li>Indeed resume intake pipeline</li>
        <li>Borough-aware contact routing</li>
        <li>White-label recruiter persona</li>
        <li>Human review queue</li>
      </ul>
    </div>
    <div class="price-card">
      <div class="price-tier">Agency Scale</div>
      <div class="price-val">Custom</div>
      <div class="price-per">Multi-location · ATS integrations</div>
      <ul class="price-feats">
        <li>Everything in Professional</li>
        <li>Multiple phone numbers / inboxes</li>
        <li>Multiple recruiter personas</li>
        <li>Bullhorn / TempWorks / Avionte API</li>
        <li>Priority support SLA</li>
        <li>Quarterly strategy review</li>
      </ul>
    </div>
  </div>
  <table class="comp-table">
    <thead><tr><th>Competing solution</th><th>Price range</th><th>What's missing vs. BlueLine</th></tr></thead>
    <tbody>
      <tr><td>Basic SMS tools (EZTexting, SimpleTexting, TextMagic)</td><td>$24–300/mo</td><td>No AI intelligence · No document review · No context awareness</td></tr>
      <tr><td>Staffing SMS automation (Sense, TextRecruit / iCIMS)</td><td>$500–1,200/mo</td><td>No document review · No healthcare-specific credential validation</td></tr>
      <tr><td>Enterprise AI screening (Hiredscore, HCI platforms)</td><td>$15,000–40,000/yr</td><td>Screening only — no outreach, no SMS, no TCPA architecture</td></tr>
      <tr><td>Manual credentialing service (per-candidate)</td><td>$25–75/candidate</td><td>Labor cost only — no scale, no outreach, no automation</td></tr>
      <tr class="highlight-row"><td>BlueLine Professional — full stack</td><td>$1,500/mo</td><td>All-in-one: outreach + context AI + doc review + TCPA + reporting</td></tr>
    </tbody>
  </table>
</div>

<!-- ═══ SLIDE 12 ═══ -->
<div class="slide" id="slide-12">
  <div class="slide-tag">Close · 29:00 – 30:00</div>
  <h2>You Can Be Live in 5 Business Days.</h2>
  <div class="deck-sub">No IT department. No six-month onboarding. No learning curve. Here's exactly how it works — with your systems, your number, your list.</div>
  <div class="onboard-grid">
    <div class="onboard-step">
      <div class="onboard-num">1</div>
      <div>
        <div class="onboard-title">Day 1 — Kickoff Call (45 min)</div>
        <div class="onboard-body">You share your candidate list and connect your agency's SMS number. We configure your recruiter persona, message templates, borough routing, and pay rates.</div>
        <div class="onboard-tools">SMS platforms: OpenPhone, Podium, Twilio, EZTexting · Email: Gmail, Outlook</div>
      </div>
    </div>
    <div class="onboard-step">
      <div class="onboard-num">2</div>
      <div>
        <div class="onboard-title">Days 2–3 — Supervised Testing</div>
        <div class="onboard-body">We test on 10 real candidates from your list. You watch every action before it touches anyone at scale. Nothing goes live without your sign-off.</div>
        <div class="onboard-tools">Candidate list from: Indeed CSV, LinkedIn, TempWorks / Bullhorn export, spreadsheet</div>
      </div>
    </div>
    <div class="onboard-step">
      <div class="onboard-num">3</div>
      <div>
        <div class="onboard-title">Day 4 — First Live Run</div>
        <div class="onboard-body">You're on a call watching every action in real time. 30 leads contacted. Email drafts appear in your inbox. Run log delivered. Zero surprises.</div>
        <div class="onboard-tools">Outputs: SMS platform outbox · Gmail/Outlook drafts · Run log CSV</div>
      </div>
    </div>
    <div class="onboard-step">
      <div class="onboard-num" style="background:var(--green-border);">4</div>
      <div>
        <div class="onboard-title">Day 5 — Handover</div>
        <div class="onboard-body">The agent runs at 8 AM from this morning forward. You review any email drafts before sending. That is your entire daily task.</div>
        <div class="onboard-tools">Ongoing outputs: daily run CSV · email drafts · human review queue · SMS outbox</div>
      </div>
    </div>
  </div>
  <div class="close-vision">
    <div class="cv-text">
      Two weeks from today — you wake up to:<br>
      <strong style="color:#fff;">30 nurses contacted · 5 active conversations · 2 document reviews drafted</strong><br>
      Without your team doing any of it.
    </div>
    <div class="cv-cta">
      <div class="cv-cta-big">$143,640</div>
      <div class="cv-cta-sub">True annual advantage<br>vs. one human recruiter</div>
    </div>
  </div>
</div>

</div><!-- slide-viewport -->
<div class="nav-area">
  <button class="nav-btn" id="prevBtn" onclick="goSlide(cur-1)" disabled>← Previous</button>
  <div class="nav-dots" id="navDots"></div>
  <button class="nav-btn" id="nextBtn" onclick="goSlide(cur+1)">Next →</button>
</div>
</div><!-- slide-panel -->

<div class="notes-panel" id="notesPanel">
  <div class="notes-header">📋 Speaker Notes</div>
  <div class="notes-content" id="notesContent"></div>
</div>
</div><!-- main-area -->

<script>
const TOTAL=12;let cur=1,autoPlaying=false,autoTimer=null,narrationOn=true,selTierVal='starter';

const NOTES={
1:{time:"0:00–2:00",content:`<h3>Opening Hook</h3><div class="exact">"What you're looking at is a fully automated AI recruiting agent — live, running daily, placing nurses right now."</div><ul><li>344 contacts, 41 convos, 30/day — let the stats speak first</li><li>Response time table — pause on &lt;10 sec reply vs 4.2 hrs. Let it land.</li><li>Goal: credibility established before you say another word</li></ul>`},
2:{time:"2:00–5:00",content:`<h3>Pain Points</h3><div class="exact">"Here's what your recruiter does every morning. Same message. Different number. 750 times a year."</div><ul><li>750 hrs/year = 18.75 full-time work weeks on copy-paste. Say that.</li><li>$1,500 fine headline — read it slowly, it's intentionally alarming</li><li>The VS bar: 4 hours vs 10 seconds — pause, let the contrast register</li></ul>`},
3:{time:"5:00–9:00",content:`<h3>The Full Journey</h3><div class="exact">"Six stages. Twelve to twenty hours. Thirty-six to forty-nine days. That's the real cost of one placed nurse."</div><ul><li>Stages 1–4 → BlueLine: ZERO. Say this clearly.</li><li>ASHHRA 49-day stat: cite it by name if challenged</li><li>Walk each stage — the platform tags help them relate to their own workflow</li></ul>`},
4:{time:"9:00–13:00",content:`<h3>The Real Cost</h3><div class="exact">"The salary is never the full cost. And the full cost still doesn't include the $99,000 hole that opens every year your recruiter takes a sick day."</div><ul><li>37 down days × 30 leads = 1,110 candidates never contacted</li><li>$161,640 true cost vs $18,000 BlueLine — this is the number to land</li><li class="warn">Label the $99K as conservative — note the 5% placement rate assumption</li></ul>`},
5:{time:"13:00–17:00",content:`<h3>Product Walkthrough</h3><div class="exact">"Four steps. Every morning. No human trigger. The execution order exists for a reason — inbound first, stalled second, fresh outreach last."</div><ul><li>The step ordering was redesigned to make logical sense to clients — use the rationale labels</li><li>Software names in each card = system-agnostic pitch. Works with what they already use.</li><li>If asked about ATS integration: "Agency Scale tier covers Bullhorn, TempWorks, Avionte"</li></ul>`},
6:{time:"17:00–20:00",content:`<h3>The Intelligence Differentiator</h3><div class="exact">"Every competitor fires the same blast. BlueLine reads the conversation first."</div><ul><li>Maria and James examples are both real-world patterns — use both</li><li>The context engine: SMS pull → Gmail pull → Claude decides. Walk through each.</li><li>"What AI?" → Claude by Anthropic. Same family as the model behind ChatGPT's top competitor. Enterprise-grade.</li></ul>`},
7:{time:"20:00–22:00",content:`<h3>Compliance</h3><div class="exact">"We built the compliance layer before we built the outreach engine. That's not typical."</div><ul><li>$1,500 is max fine per message — federal statute, not estimate</li><li>Human-in-loop email is a feature, not a limitation — positions you as responsible</li><li>NYS credential validation: this is the one capability competitors can't replicate without healthcare domain knowledge</li><li class="warn">If asked about HIPAA: system handles contact data only — no PHI, no clinical records</li></ul>`},
8:{time:"22:00–24:30",content:`<h3>ROI Calculator</h3><div class="exact">"Dial in your numbers. Watch the bottom of this slide update live."</div><ul><li>Default: 8 placements/mo, $38 bill rate, 35% margin, 3 shifts/wk</li><li>CNA bill rates: $18–22. LPN: $26–34. RN: $38–55. (Staffmark/CareerStaff 2023)</li><li>Let them drive the sliders — this is interactive for a reason</li><li>The large NET ADVANTAGE number at the bottom = the one number to screenshot and share</li></ul>`},
9:{time:"24:30–26:30",content:`<h3>Unit Economics</h3><div class="exact">"The question isn't what BlueLine costs. It's what each placement costs you — with and without it."</div><ul><li>Each number now has an immediate label — no math needed to understand it</li><li>Default: 1 recruiter at $62k, 8 placements/mo → $648 manual CPP</li><li>With Pro: same recruiter places 11.6/mo → CPP drops significantly</li><li>"What does one extra placement per month mean to your revenue?" — ask this out loud</li></ul>`},
10:{time:"26:30–28:00",content:`<h3>Scope</h3><div class="exact">"Eight capabilities. One price. No add-ons. No surprises after you sign."</div><ul><li>Compatible platforms listed in each card — makes it feel like it fits their existing stack</li><li>White-labelling is the highest-value feature for agencies protective of their brand</li><li>Document Intelligence: the NYS date window validation is unique — no other SMS tool does this</li></ul>`},
11:{time:"28:00–29:00",content:`<h3>Pricing</h3><div class="exact">"Professional is fifty dollars a day. Less than the cost of your recruiter sitting down and opening their laptop before they've done a single productive thing."</div><ul><li>The competitive comparison table validates our pricing — SMS-only tools charge $500–1,200 for far less</li><li>Agency Scale: don't leave on the table for multi-location agencies</li><li class="warn">Objection: "too expensive" → Back to the $143,640 true annual advantage. This is $50/day.</li><li class="warn">Objection: "need to think" → "What would you need to see to move forward today?"</li></ul>`},
12:{time:"29:00–30:00",content:`<h3>The Close</h3><div class="exact">"Five business days. Day one is 45 minutes. You give us your list and your number. We do the rest."</div><ul><li>Works with any SMS platform — OpenPhone, Podium, Twilio, EZTexting. Name theirs if you know it.</li><li>The supervised first run is the trust-builder — they watch every action before it scales</li><li>End with the two-week vision — say it slowly</li><li>Next step: "Can we schedule the Day 1 kickoff call this week?" Have your booking link ready.</li></ul>`},
};

// Nav dots
const dotsEl=document.getElementById('navDots');
for(let i=1;i<=TOTAL;i++){
  const d=document.createElement('div');
  d.className='dot'+(i===1?' active':'');
  d.onclick=(n=>()=>goSlide(n))(i);
  dotsEl.appendChild(d);
}

function renderNotes(n){
  const d=NOTES[n];if(!d)return;
  document.getElementById('notesContent').innerHTML=`<div class="notes-time">⏱ ${d.time}</div>${d.content}`;
}

function goSlide(n){
  if(n<1||n>TOTAL)return;
  document.getElementById('slide-'+cur).classList.remove('active');
  cur=n;
  document.getElementById('slide-'+cur).classList.add('active');
  document.getElementById('slideCounter').textContent=cur+' / '+TOTAL;
  document.getElementById('progressFill').style.width=(cur/TOTAL*100)+'%';
  document.getElementById('prevBtn').disabled=(cur===1);
  document.getElementById('nextBtn').disabled=(cur===TOTAL);
  document.querySelectorAll('.dot').forEach((d,i)=>d.classList.toggle('active',i+1===cur));
  renderNotes(cur);
  if(cur===8)setTimeout(calcROI,150);
  if(cur===9)setTimeout(calcCPP,150);
  if(narrationOn)playNarration(cur);
}

function toggleNotes(){
  const p=document.getElementById('notesPanel'),b=document.getElementById('notesBtn');
  const open=p.classList.toggle('open');b.classList.toggle('active',open);renderNotes(cur);
}
function toggleAutoPlay(){
  const btn=document.getElementById('playBtn');
  if(autoPlaying){clearInterval(autoTimer);autoPlaying=false;btn.textContent='▶ Auto-Play';}
  else{autoPlaying=true;btn.textContent='⏸ Pause';
    autoTimer=setInterval(()=>{if(cur<TOTAL)goSlide(cur+1);else{clearInterval(autoTimer);autoPlaying=false;btn.textContent='▶ Auto-Play';}},14000);
  }
}

/* ── ROI CALC ── */
function calcROI(){
  const placed=+document.getElementById('sliderPlaced').value;
  const bill=+document.getElementById('sliderBill').value;
  const margin=+document.getElementById('sliderMargin').value/100;
  const shifts=+document.getElementById('sliderShifts').value;
  document.getElementById('cPlaced').textContent=placed;
  document.getElementById('cBill').textContent='$'+bill;
  document.getElementById('cMargin').textContent=Math.round(margin*100)+'%';
  document.getElementById('cShifts').textContent=shifts;

  const blCost=18000;
  const wkHrs=shifts*8;

  // ① Placement lift — +25% more placements from faster response and follow-up
  const cur_margin=placed*wkHrs*52*bill*margin;
  const gain_placements=Math.round(cur_margin*0.25); // 25% lift

  // ② Downtime coverage — 37 missed days × 30 leads × 5% placement rate
  // Per-placement gross margin = shifts × 8hrs × 6 weeks × bill × margin (conservative 6-wk avg)
  const per_placement=Math.round(shifts*8*6*bill*margin);
  const gain_downtime=Math.round(1110*0.05*per_placement);

  // ③ Recruiter time freed — 750 hrs/yr manual outreach eliminated
  // Conservative value: $30/hr effective cost (portion of $62K salary)
  const gain_time=22500;

  const total_gain=gain_placements+gain_downtime+gain_time;
  const net=total_gain-blCost;
  const payback=blCost/((total_gain)/12);

  document.getElementById('rGainPlacements').textContent='+$'+Math.round(gain_placements/1000)+'K/yr';
  document.getElementById('rGainDowntime').textContent='+$'+Math.round(gain_downtime/1000)+'K/yr';
  document.getElementById('rPayback').textContent=payback<1?'< 1 month':Math.round(payback*10)/10+' months';

  const bigEl=document.getElementById('impactBig');
  bigEl.classList.remove('popping');void bigEl.offsetWidth;
  const netK=Math.round(net/1000);
  bigEl.textContent='+'+'$'+netK+'K/yr';
  bigEl.classList.add('popping');

  document.getElementById('ibPlacement').textContent='+$'+Math.round(gain_placements/1000)+'K';
  document.getElementById('ibDowntime').textContent='+$'+Math.round(gain_downtime/1000)+'K';
}

/* ── CPP CALC ── */
function selTier(t){
  selTierVal=t;
  document.getElementById('tS').classList.toggle('selected',t==='starter');
  document.getElementById('tP').classList.toggle('selected',t==='pro');
  calcCPP();
}
function calcCPP(){
  const rc=+document.getElementById('slRC').value;
  const cost=+document.getElementById('slCost').value;
  const pl=+document.getElementById('slPl').value;
  const blMo=selTierVal==='starter'?800:1500;
  document.getElementById('cpRC').textContent=rc;
  document.getElementById('cpCost').textContent='$'+Math.round(cost/1000)+'K';
  document.getElementById('cpPl').textContent=pl;
  const totalCost=rc*cost;
  const totalPl=rc*pl;
  const manCPP=Math.round(totalCost/totalPl/12);
  const aiPl=Math.round(totalPl*1.45);
  const aiTotalCost=totalCost+blMo*12;
  const aiCPP=Math.round(aiTotalCost/aiPl/12);
  const extra=aiPl-totalPl;
  const saving=Math.round((manCPP-aiCPP)*aiPl*12);
  document.getElementById('rManualCPP').textContent='$'+manCPP;
  document.getElementById('rAICPP').textContent='$'+aiCPP;
  document.getElementById('rExtra').textContent='+'+extra+' extra/mo';
  document.getElementById('rSaving').textContent='$'+Math.round(saving/1000)+'K/yr';
}

/* ── NARRATION (Web Speech placeholder) ── */
const NAR=[
  '',
  "Welcome. What you're looking at is a fully automated AI recruiting agent built specifically for nursing homes and rehabilitation centers. It's not a concept. It's live, running daily, placing nurses now. It reaches out to thirty new nurses every morning. It responds to an interested candidate in under ten seconds. It has never once accidentally re-contacted someone who asked to be left alone.",
  "Here's what your recruiter does every morning. They open their laptop. They pull up their candidate list. And for the next two to three hours, they copy and paste the same intro message — one nurse at a time. Seven hundred and fifty hours a year on pure repetition. And forty percent of candidates who say yes never make it to a shift — because the average agency response time is four hours. The average nurse response window to an SMS is ninety seconds. By the time your recruiter replies, she has accepted a shift at a competing agency.",
  "Let me walk you through what it actually takes to place a single nurse. Six stages. Twelve to twenty hours. Thirty-six to forty-nine days. Stages one through four — lead discovery, info collection, portal entry, and the full candidate communication sequence — BlueLine takes all of these to zero. The first four stages: completely automated. Stages five and six still need a human, but BlueLine does eighty-three percent of the document work automatically. The result is two hours of recruiter time instead of twenty. And a placement in twenty-five days instead of forty-nine.",
  "Let's talk numbers. A recruiter doing this work manually costs your agency sixty-two thousand six hundred and forty dollars a year. But here's the number that's never in the proposal. The average US recruiter is out of the office thirty-seven days per year. Sick days. Vacation. Unscheduled absences. Federal holidays. Fourteen percent of the work year — paid in full, with zero output. On those thirty-seven days, no outreach goes out. Eleven hundred candidates are never contacted. At a five percent placement rate, that is fifty-five missed placements and roughly ninety-nine thousand dollars in missed gross margin. Every year. The true annual cost of one human recruiter: one hundred and sixty-one thousand dollars. BlueLine: eighteen thousand. Runs three hundred and sixty-five days. Zero sick days. Zero vacation. Zero holidays.",
  "The agent runs four steps every morning. No human trigger required. Step one: Document Review. Before your team opens their email, AI Vision has already read every nurse's credential documents, checked each one against New York State date windows, and drafted a reply. Step two: SMS Reply Handling. A YES gets the document checklist in under ten seconds. A STOP triggers a permanent block instantly. Step three: Re-engagement. Any candidate silent for four or more days gets a personalised follow-up — after the system reads their last four days of conversation history. Step four: New Lead Outreach. Thirty fresh candidates every morning. Every contact cross-checked against all existing records. Zero duplicates.",
  "This is what separates BlueLine from every other automation tool. Every platform fires the same blast to every number and waits. BlueLine reads the conversation before it sends anything. Maria submitted her documents two days ago. Standard automation sends her: are you still interested? She already proved she was interested. She now thinks no one looked at what she sent. What BlueLine sends instead: just checking in — you sent your documents over on Monday, our team is reviewing and will be in touch by Thursday. That is the difference between losing a candidate and keeping her. And that decision happens automatically — for every candidate — every single morning.",
  "Healthcare staffing carries one of the highest TCPA liability profiles of any industry. We built the compliance layer before we built the outreach engine. When a nurse texts STOP, her number is written to a permanent file that survives system restarts, database resets, and CSV re-imports. There is no workflow — no import, no API call, no manual action — that gets that number back into the system. Every email reply is saved as a draft. A human reviews it and sends it. And every single action is logged with a timestamp. One TCPA violation is fifteen hundred dollars. This architecture makes accidental re-contact structurally impossible.",
  "Use the sliders to dial in your agency's actual figures. A twenty-five percent improvement in placement rate — conservative, most agencies see this within sixty days from faster follow-up alone — generates additional annual gross margin that dwarfs the eighteen-thousand-dollar system cost. Watch the net advantage number at the bottom of this slide update as you move. That number — the green one — is your year-one profit from making this switch.",
  "Let's look at this through a different lens. Cost per placement. With one recruiter at sixty-two thousand a year placing eight nurses a month, your cost per placement is around six hundred and fifty dollars. Add BlueLine and that same recruiter handles forty-five percent more placements — because the entire outreach and follow-up workload is automated. Each number on the right side of this slide tells you exactly what that means in plain language.",
  "Eight capabilities. One price. No modules to purchase separately. And the system is built to work with your existing stack — your SMS platform, your email client, your candidate sources. Candidates never know this system exists. As far as they are concerned, they are texting your recruiter.",
  "Three tiers. Starter at eight hundred a month. Professional at fifteen hundred — that is fifty dollars a day, less than the cost of your recruiter sitting down before they have done a single productive thing. Agency Scale for multi-location operations. The comparison table at the bottom shows what competitors charge for tools that do a fraction of what BlueLine does.",
  "Five business days. Day one is forty-five minutes — you share your candidate list and connect your agency's number. We configure everything else. Days two and three: we test on ten real candidates. You watch every action before it scales. Day four: the first live run. Day five: handover. The agent runs at eight AM every morning from that point forward. Two weeks from today, you wake up to thirty nurses contacted, five active conversations, and two document reviews drafted — without your team doing any of it.",
];

const synth=window.speechSynthesis;
let utter=null;
function playNarration(n){
  if(!narrationOn||!NAR[n])return;
  synth.cancel();
  utter=new SpeechSynthesisUtterance(NAR[n]);
  utter.rate=0.92;utter.pitch=1.0;utter.volume=1.0;
  const voices=synth.getVoices();
  const v=voices.find(v=>v.name.includes('Samantha')||v.name.includes('Google US English')||v.lang==='en-US');
  if(v)utter.voice=v;
  synth.speak(utter);
}
function toggleNarration(){
  narrationOn=!narrationOn;
  const btn=document.getElementById('narrationBtn');
  if(narrationOn){btn.textContent='🔊 Narration On';btn.style.background='var(--blue)';}
  else{btn.textContent='🔇 Narration Off';btn.style.background='var(--dim)';synth.cancel();}
}
document.addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key==='ArrowDown')goSlide(cur+1);
  if(e.key==='ArrowLeft'||e.key==='ArrowUp')goSlide(cur-1);
});
if(synth.onvoiceschanged!==undefined)synth.onvoiceschanged=()=>synth.getVoices();
synth.getVoices();
renderNotes(1);calcROI();calcCPP();
</script>
</body>
</html>"""

with open(OUT,'w',encoding='utf-8') as f:
    f.write(HTML)
size_kb=os.path.getsize(OUT)//1024
print(f"Written: {OUT}")
print(f"Size: {size_kb} KB")
print("Next: python3.11 gen_all_audio.py && python3.11 embed_audio.py")
