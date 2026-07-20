"""
Builds blueline_architecture_doc.html — v2 with:
  - Healthcare Recruitment Journey section (top)
  - Agency Cost Calculator
  - All existing animated pipeline sections
  - Web Speech API placeholder (replaced by ElevenLabs via build_arch_audio.py)

[DEPRECATED 2026-07-02, Round 6 audit — DO NOT RUN EXPECTING A LIVE-DOC REFRESH]
Same finding as build_pitch_deck.py (see that file). This script hardcodes
stale content ("v2.1", "13 bugs fixed") predating the v3.0 24/7 real-time
layer, and the real, presented file (dylan_for_hire_architecture.html) has
embedded ElevenLabs audio this script does not generate. OUT redirected below
so running this can never silently regress the real file. See
DYLAN_AUDIT_2026-07-01_FULL.md Round 6 and 09_GO_LIVE_READINESS.md KNOWN GAPS.
"""
import os

# [FIX 2026-07-02] Was ~/Downloads/BlueLine/blueline_architecture_doc.html.
OUT = os.path.expanduser("~/Downloads/BlueLine/DEPRECATED_DO_NOT_USE_blueline_architecture_doc.html")

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BlueLine Staffing AI Agent — Architecture</title>
<style>
:root{
  --bg:#0a0c14;--card:#12151f;--card2:#1a1d2a;--border:#252840;
  --accent:#4f6ef7;--green:#34d399;--amber:#f59e0b;--red:#ef4444;
  --pink:#f9a8d4;--purple:#7c3aed;--text:#e2e8f0;--muted:#4a5568;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:15px;padding:24px 28px 48px;min-height:100vh;overflow-x:hidden;}
/* header */
.header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px;}
h1{font-size:22px;font-weight:700;color:#fff;margin-bottom:4px;}
.subtitle{color:var(--muted);font-size:13px;}
.version-pill{background:#0d2e1e;color:var(--green);font-size:12px;font-weight:700;padding:5px 14px;border-radius:20px;border:1px solid #1a4a30;}
/* controls */
.controls{display:flex;align-items:center;gap:10px;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:10px 16px;margin-bottom:14px;}
.ctrl-btn{background:var(--card2);border:1px solid var(--border);color:var(--text);padding:7px 16px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;transition:all .15s;white-space:nowrap;}
.ctrl-btn:hover{background:#252840;border-color:var(--accent);}
.ctrl-btn.active{background:var(--accent);border-color:var(--accent);color:#fff;}
.progress-wrap{flex:1;height:4px;background:var(--card2);border-radius:4px;overflow:hidden;}
.progress-bar{height:100%;background:var(--accent);width:0%;transition:width .25s linear;border-radius:4px;}
.step-label{font-size:12px;color:var(--muted);white-space:nowrap;min-width:180px;text-align:right;}
/* narration */
.narration{background:#0d1021;border:1px solid var(--accent);border-radius:10px;padding:12px 18px;margin-bottom:16px;font-size:14px;color:#a5b4fc;line-height:1.65;min-height:44px;display:flex;align-items:center;gap:10px;}
.nar-icon{font-size:18px;flex-shrink:0;}
.nar-text{flex:1;}
.wave{display:flex;gap:3px;align-items:center;flex-shrink:0;}
.wave span{display:block;width:3px;border-radius:2px;background:var(--accent);animation:wave-bar 1.2s ease-in-out infinite;}
.wave span:nth-child(1){height:8px;animation-delay:0s;}.wave span:nth-child(2){height:14px;animation-delay:.15s;}
.wave span:nth-child(3){height:10px;animation-delay:.3s;}.wave span:nth-child(4){height:16px;animation-delay:.45s;}
.wave span:nth-child(5){height:8px;animation-delay:.6s;}
@keyframes wave-bar{0%,100%{transform:scaleY(1);opacity:.5;}50%{transform:scaleY(1.6);opacity:1;}}
.wave.hidden{visibility:hidden;}
/* section labels */
.section-label{font-size:11px;font-weight:700;letter-spacing:1.5px;color:var(--muted);text-transform:uppercase;margin-bottom:12px;display:flex;align-items:center;gap:8px;transition:color .4s;}
.section-label::after{content:'';flex:1;height:1px;background:var(--border);transition:background .4s;}
.section-label.lit{color:var(--accent);}
.section-label.lit::after{background:var(--accent);}
/* ZOOM ANIMATION — active section expands, others shrink */
.section{transition:opacity .5s ease,transform .5s ease,font-size .5s ease;transform-origin:top center;}
.section.dimmed{opacity:0.2;transform:scale(0.94);pointer-events:none;}
.section.active-zoom{
  transform:scale(1.04);
  font-size:1.28em;
  background:rgba(79,110,247,.03);
  border-radius:18px;
  padding:18px 20px;
  box-shadow:0 0 40px rgba(79,110,247,.08),0 0 0 1px rgba(79,110,247,.12);
  position:relative;z-index:5;
}
.gap{height:14px;}
/* ── RECRUITMENT JOURNEY ── */
.journey-header{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:10px;}
.journey-stages{display:grid;grid-template-columns:repeat(6,1fr);gap:0;position:relative;}
.journey-stages::before{content:'';position:absolute;top:22px;left:34px;right:34px;height:2px;background:var(--border);z-index:0;}
.j-stage{display:flex;flex-direction:column;align-items:center;text-align:center;position:relative;z-index:1;}
.j-num{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;border:2px solid var(--accent);background:#0d1021;color:var(--accent);margin-bottom:7px;transition:border-color .4s,box-shadow .4s,background .4s;}
.j-stage.lit .j-num{background:var(--accent);color:#fff;box-shadow:0 0 14px rgba(79,110,247,.4);}
.j-title{font-size:10px;font-weight:700;color:var(--text);margin-bottom:4px;}
.j-manual{font-size:9px;color:var(--red);font-weight:600;margin-bottom:2px;}
.j-ai{font-size:9px;color:var(--green);font-weight:700;margin-bottom:4px;}
.j-tags{display:flex;flex-wrap:wrap;gap:2px;justify-content:center;}
.j-tag{font-size:8px;padding:1px 5px;border-radius:8px;background:#1e2d45;color:var(--muted);}
/* journey table */
.journey-table{margin-top:10px;border-radius:10px;overflow:hidden;border:1px solid var(--border);}
.jt-row{display:grid;grid-template-columns:2.5fr 1fr 1fr 1fr;}
.jt-header .jt-cell{background:#0d1021;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);}
.jt-cell{padding:7px 12px;font-size:11px;border-bottom:1px solid var(--border);border-right:1px solid var(--border);}
.jt-cell:last-child{border-right:none;}
.jt-row:last-child .jt-cell{border-bottom:none;font-weight:700;background:#0a0f1f;}
.src-note{font-size:9px;color:var(--muted);margin-top:6px;font-style:italic;line-height:1.6;}
/* ── DOWNTIME TABLE ── */
.downtime-section{margin-top:10px;}
.dt-label{font-size:10px;font-weight:700;color:var(--amber);text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;display:flex;align-items:center;gap:6px;}
.dt-label::after{content:'';flex:1;height:1px;background:#4a3000;}
.dt-grid{display:grid;grid-template-columns:1.8fr .6fr .6fr 1.6fr;border:1px solid #4a3000;border-radius:8px;overflow:hidden;margin-bottom:8px;}
.dt-hdr .dt-cell{background:#1c1205;font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:#78350f;}
.dt-cell{padding:6px 10px;font-size:10px;border-bottom:1px solid #2a1a00;border-right:1px solid #2a1a00;}
.dt-cell:last-child{border-right:none;}
.dt-total .dt-cell{border-bottom:none;font-weight:700;background:#1c1205;}
.dt-impacts{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px;}
.dt-impact{background:var(--card);border:1px solid #78350f;border-radius:8px;padding:9px 11px;text-align:center;}
.dt-impact-num{font-size:18px;font-weight:800;color:var(--amber);margin-bottom:2px;}
.dt-impact-label{font-size:9px;color:var(--muted);}
.dt-true-cost{background:#1c0a0a;border:1px solid #7f1d1d;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;}
.dt-tc-left{font-size:10px;color:#fca5a5;line-height:1.7;}
.dt-tc-right{text-align:right;}
.dt-tc-num{font-size:22px;font-weight:800;color:var(--red);}
.dt-tc-vs{font-size:10px;color:var(--green);font-weight:700;margin-top:2px;}
/* ── AGENCY CALCULATOR ── */
.cpp-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:0;}
.cpp-inputs{display:flex;flex-direction:column;gap:8px;}
.cpp-results{display:flex;flex-direction:column;gap:8px;}
.calc-group{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:11px 14px;}
.calc-label{font-size:10px;color:var(--muted);margin-bottom:5px;}
.calc-val-sm{font-size:20px;font-weight:700;color:var(--accent);margin-bottom:3px;}
.calc-slider{width:100%;accent-color:var(--accent);margin-top:2px;}
.cpp-insight{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:11px 14px;transition:border-color .4s,box-shadow .4s;}
.cpp-insight.red{border-color:#7f1d1d;}
.cpp-insight.green{border-color:#065f46;}
.cpp-insight.amber{border-color:#78350f;}
.cpp-insight.purple{border-color:#3b1d6e;}
.cpp-insight-num{font-size:26px;font-weight:800;margin-bottom:3px;}
.cpp-insight-label{font-size:11px;color:var(--muted);}
.cpp-insight-sub{font-size:9px;color:var(--muted);margin-top:2px;opacity:.7;}
.tier-toggle{display:flex;gap:6px;margin-top:6px;}
.tier-btn{flex:1;padding:6px;border-radius:7px;font-size:10px;font-weight:600;cursor:pointer;border:1px solid var(--border);background:var(--card2);color:var(--muted);transition:all .15s;text-align:center;}
.tier-btn.selected{background:#0d1021;border-color:var(--accent);color:#a5b4fc;}
.cpp-assumption{font-size:9px;color:var(--muted);margin-top:8px;padding:7px 10px;background:#0a0c14;border-radius:7px;line-height:1.6;border:1px solid var(--border);}
/* ── FLOW ARROWS ── */
.flow-track{position:relative;overflow:hidden;display:flex;flex-direction:column;align-items:center;height:30px;justify-content:center;margin:4px 0;}
.flow-track svg{position:relative;z-index:2;}
@keyframes flow-down{0%{top:-8px;opacity:1;}80%{opacity:1;}100%{top:38px;opacity:0;}}
.particle{position:absolute;width:7px;height:7px;border-radius:50%;left:calc(50% - 3.5px);animation:flow-down .85s ease-in forwards;pointer-events:none;}
/* ── SOURCE CARDS ── */
.inputs-row{display:flex;gap:10px;flex-wrap:wrap;}
.source-card{flex:1;min-width:140px;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:13px 14px;transition:border-color .4s,box-shadow .4s,transform .3s;}
.source-card.lit{border-color:var(--accent);box-shadow:0 0 16px rgba(79,110,247,.25);transform:translateY(-2px);}
.source-card .icon{font-size:22px;margin-bottom:8px;}
.source-card .title{font-weight:700;font-size:14px;margin-bottom:4px;}
.source-card .detail{font-size:12px;color:var(--muted);line-height:1.6;}
/* ── ENGINE ── */
.engine{background:var(--card);border:1.5px solid var(--accent);border-radius:14px;padding:16px 18px;transition:box-shadow .4s;}
.engine.lit{box-shadow:0 0 28px rgba(79,110,247,.2);}
.engine-title{font-size:12px;font-weight:700;color:var(--accent);margin-bottom:12px;display:flex;align-items:center;gap:8px;}
.steps-grid{display:flex;gap:8px;flex-wrap:wrap;}
.step{flex:1;min-width:150px;background:var(--card2);border:1px solid var(--border);border-radius:10px;padding:11px 12px;position:relative;overflow:hidden;transition:border-color .4s,box-shadow .4s,transform .3s;}
.step::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:currentColor;opacity:0;transition:opacity .4s;}
.step.s0{color:var(--green);}.step.s3{color:var(--accent);}
.step.s1{color:var(--amber);}.step.s2{color:var(--pink);}
.step.s0.lit{border-color:var(--green);box-shadow:0 0 14px rgba(52,211,153,.2);transform:translateY(-2px);}
.step.s3.lit{border-color:var(--accent);box-shadow:0 0 14px rgba(79,110,247,.25);transform:translateY(-2px);}
.step.s1.lit{border-color:var(--amber);box-shadow:0 0 14px rgba(245,158,11,.2);transform:translateY(-2px);}
.step.s2.lit{border-color:var(--pink);box-shadow:0 0 14px rgba(249,168,212,.2);transform:translateY(-2px);}
.step.lit::before{opacity:1;}
.step-num{font-size:12px;font-weight:700;letter-spacing:1px;margin-bottom:4px;}
.step-name{font-weight:700;font-size:14px;margin-bottom:6px;color:var(--text);}
.step-detail{font-size:12px;color:var(--muted);line-height:1.65;}
/* ── INTELLIGENCE ── */
.logic-row{display:flex;gap:10px;flex-wrap:wrap;}
.logic-card{flex:1;min-width:140px;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:11px 13px;transition:border-color .4s,box-shadow .4s,transform .3s;}
.logic-card.lit{border-color:var(--purple);box-shadow:0 0 16px rgba(124,58,237,.2);transform:translateY(-2px);}
.logic-card .lc-title{font-weight:700;font-size:14px;margin-bottom:8px;}
.logic-card .lc-body{font-size:12px;color:var(--muted);line-height:1.7;}
.badge{display:inline-block;padding:2px 7px;border-radius:20px;font-size:9px;font-weight:700;margin-right:3px;margin-bottom:3px;}
.badge-blue{background:#1e3a8a;color:#93c5fd;}.badge-green{background:#064e3b;color:#6ee7b7;}
.badge-amber{background:#78350f;color:#fcd34d;}.badge-red{background:#7f1d1d;color:#fca5a5;}
/* ── OUTPUTS ── */
.outputs-row{display:flex;gap:10px;flex-wrap:wrap;}
.out-card{flex:1;min-width:110px;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:11px 12px;text-align:center;transition:border-color .4s,box-shadow .4s,transform .3s;}
.out-card.lit{border-color:var(--green);box-shadow:0 0 16px rgba(52,211,153,.2);transform:translateY(-2px);}
.out-icon{font-size:20px;margin-bottom:4px;}
.out-title{font-weight:700;font-size:14px;margin-bottom:4px;}
.out-detail{font-size:12px;color:var(--muted);}
/* ── METRICS ── */
.metrics{display:flex;gap:10px;flex-wrap:wrap;}
.metric{flex:1;min-width:85px;background:var(--card2);border:1px solid var(--border);border-radius:10px;padding:11px 12px;text-align:center;transition:border-color .4s,box-shadow .4s;}
.metric.lit{border-color:var(--accent);box-shadow:0 0 12px rgba(79,110,247,.15);}
.metric-num{font-size:26px;font-weight:800;color:var(--accent);}
.metric-label{font-size:12px;color:var(--muted);margin-top:3px;}
/* ── COMPLIANCE ── */
.compliance{background:#12100a;border:1px solid #4a3000;border-radius:12px;padding:11px 14px;display:flex;gap:18px;flex-wrap:wrap;align-items:flex-start;transition:border-color .4s,box-shadow .4s;}
.compliance.lit{border-color:var(--amber);box-shadow:0 0 16px rgba(245,158,11,.15);}
.compliance .ct{font-size:13px;font-weight:700;color:#fbbf24;margin-bottom:4px;}
.compliance .ci{font-size:12px;color:#92620a;line-height:1.7;}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div>
    <h1>BlueLine Staffing AI Agent</h1>
    <div class="subtitle">Automated healthcare staffing pipeline — NYC · v2.1 · 2026-06-29</div>
  </div>
  <span class="version-pill">13 bugs fixed</span>
</div>

<!-- CONTROLS -->
<div class="controls">
  <button class="ctrl-btn" id="playBtn" onclick="togglePlay()">▶ Play</button>
  <button class="ctrl-btn" onclick="restart()">↺ Restart</button>
  <div class="progress-wrap"><div class="progress-bar" id="progressBar"></div></div>
  <div class="step-label" id="stepLabel">Ready</div>
</div>
<div class="narration">
  <span class="nar-icon">🔊</span>
  <span class="nar-text" id="narText">Press Play to walk through the pipeline with audio narration.</span>
  <div class="wave hidden" id="waveEl"><span></span><span></span><span></span><span></span><span></span></div>
</div>

<!-- ═══════════════════════════════════════════ -->
<!-- SECTION A: RECRUITMENT JOURNEY             -->
<!-- ═══════════════════════════════════════════ -->
<div class="section" id="sec-journey">
  <div class="section-label" id="lbl-journey">The Healthcare Recruitment Journey</div>
  <div class="journey-stages">
    <div class="j-stage" id="jstg1">
      <div class="j-num">1</div>
      <div class="j-title">Lead Discovery</div>
      <div class="j-manual">Manual: 5–15 min</div>
      <div class="j-ai">AI: 0 min ✓</div>
      <div class="j-tags">
        <span class="j-tag">Indeed</span><span class="j-tag">LinkedIn</span>
        <span class="j-tag">ZipRecruiter</span><span class="j-tag">Vivian</span>
        <span class="j-tag">CSV list</span><span class="j-tag">Referral</span>
      </div>
    </div>
    <div class="j-stage" id="jstg2">
      <div class="j-num">2</div>
      <div class="j-title">Info Assimilation</div>
      <div class="j-manual">Manual: 10–20 min</div>
      <div class="j-ai">AI: 0 min ✓</div>
      <div class="j-tags">
        <span class="j-tag">License type</span><span class="j-tag">Specialty</span>
        <span class="j-tag">Location</span><span class="j-tag">Availability</span>
      </div>
    </div>
    <div class="j-stage" id="jstg3">
      <div class="j-num">3</div>
      <div class="j-title">ATS / Portal Entry</div>
      <div class="j-manual">Manual: 15–30 min</div>
      <div class="j-ai">AI: 0 min ✓</div>
      <div class="j-tags">
        <span class="j-tag">Bullhorn</span><span class="j-tag">TempWorks</span>
        <span class="j-tag">Avionte</span><span class="j-tag">OpenPhone</span>
        <span class="j-tag">Spreadsheet</span>
      </div>
    </div>
    <div class="j-stage" id="jstg4">
      <div class="j-num">4</div>
      <div class="j-title">Candidate Comms</div>
      <div class="j-manual">Manual: 2–4 hrs</div>
      <div class="j-ai">AI: 0 min ✓</div>
      <div class="j-tags">
        <span class="j-tag">5–7 touches avg</span>
        <span class="j-tag">SMS</span><span class="j-tag">Email</span><span class="j-tag">Phone</span>
        <span class="j-tag">2–3 weeks</span>
      </div>
    </div>
    <div class="j-stage" id="jstg5">
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
    <div class="j-stage" id="jstg6">
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
    <div class="jt-row jt-header">
      <div class="jt-cell">Stages</div>
      <div class="jt-cell">Manual time</div>
      <div class="jt-cell">With BlueLine</div>
      <div class="jt-cell">Reduction</div>
    </div>
    <div class="jt-row">
      <div class="jt-cell">Stages 1–4 · Lead → Comms</div>
      <div class="jt-cell" style="color:var(--red);">3–5 hrs</div>
      <div class="jt-cell" style="color:var(--green);">0 min</div>
      <div class="jt-cell" style="color:var(--green);font-weight:700;">−100%</div>
    </div>
    <div class="jt-row">
      <div class="jt-cell">Stage 5 · Document review</div>
      <div class="jt-cell" style="color:var(--red);">45–90 min</div>
      <div class="jt-cell" style="color:var(--green);">10–15 min</div>
      <div class="jt-cell" style="color:var(--green);font-weight:700;">−83%</div>
    </div>
    <div class="jt-row">
      <div class="jt-cell">Stage 6 · Credentialing + submit</div>
      <div class="jt-cell" style="color:var(--red);">2–4 hrs</div>
      <div class="jt-cell" style="color:var(--amber);">~90 min</div>
      <div class="jt-cell" style="color:var(--amber);font-weight:700;">−60%</div>
    </div>
    <div class="jt-row">
      <div class="jt-cell">Total per placed nurse · time-to-fill</div>
      <div class="jt-cell" style="color:var(--red);">12–20 hrs · 36–49 days</div>
      <div class="jt-cell" style="color:var(--green);">~2 hrs · 25–32 days</div>
      <div class="jt-cell" style="color:var(--green);">~85% reduction</div>
    </div>
  </div>
  <div class="src-note">Sources: ASHHRA 2022 Annual Workforce Survey (time-to-fill RN: 49 days) · SHRM Talent Acquisition Benchmark 2023 (manual outreach time) · InsideSales / MIT HBR (5–7 follow-up touches) · NYS DOH credential requirements (document scope) · CTIA 2023 (SMS response 90 seconds avg)</div>
</div>

<div class="gap"></div>

<!-- ═══════════════════════════════════════════ -->
<!-- SECTION B1: RECRUITER DOWNTIME COST        -->
<!-- ═══════════════════════════════════════════ -->
<div class="section" id="sec-downtime">
  <div class="section-label" id="lbl-downtime">Hidden Cost — Recruiter Downtime</div>
  <div class="downtime-section">
    <div class="dt-label">⏸ Average US recruiter: 37 unproductive days per year (14.2% of work year)</div>
    <div class="dt-grid">
      <div class="dt-hdr"><div class="dt-cell">Absence type</div><div class="dt-cell">Days/yr</div><div class="dt-cell">% of year</div><div class="dt-cell">Source</div></div>
      <div><div class="dt-cell">Sick days used</div><div class="dt-cell" style="color:var(--amber);">7.7</div><div class="dt-cell" style="color:var(--muted);">3.0%</div><div class="dt-cell" style="color:var(--muted);font-size:9px;">BLS National Compensation Survey 2023</div></div>
      <div><div class="dt-cell">Vacation (1–5yr tenure)</div><div class="dt-cell" style="color:var(--amber);">12</div><div class="dt-cell" style="color:var(--muted);">4.6%</div><div class="dt-cell" style="color:var(--muted);font-size:9px;">BLS Employee Benefits Survey 2023</div></div>
      <div><div class="dt-cell">Unscheduled absences</div><div class="dt-cell" style="color:var(--amber);">7.3</div><div class="dt-cell" style="color:var(--muted);">2.8%</div><div class="dt-cell" style="color:var(--muted);font-size:9px;">SHRM Absence Management Survey 2023</div></div>
      <div><div class="dt-cell">Paid federal holidays</div><div class="dt-cell" style="color:var(--amber);">10</div><div class="dt-cell" style="color:var(--muted);">3.8%</div><div class="dt-cell" style="color:var(--muted);font-size:9px;">OPM standard / common employer match</div></div>
      <div class="dt-total"><div class="dt-cell">Total unproductive days/yr</div><div class="dt-cell" style="color:var(--red);">37</div><div class="dt-cell" style="color:var(--red);">14.2%</div><div class="dt-cell" style="color:var(--green);font-size:9px;">BlueLine: 0 days — runs 365 days/yr</div></div>
    </div>
    <div class="dt-impacts">
      <div class="dt-impact"><div class="dt-impact-num">$8,910</div><div class="dt-impact-label">Paid salary for 37 days — zero output (fully loaded)</div></div>
      <div class="dt-impact"><div class="dt-impact-num">1,110</div><div class="dt-impact-label">Candidate contacts missed (37 days × 30 leads/day)</div></div>
      <div class="dt-impact"><div class="dt-impact-num">~$99K</div><div class="dt-impact-label">Missed gross margin (~55 lost placements at $1,800 avg)</div></div>
    </div>
    <div class="dt-true-cost">
      <div class="dt-tc-left">
        Direct compensation + overhead: $62,640<br>
        Paid unproductive time: $8,910<br>
        Missed placement revenue (conservative): ~$99,000
      </div>
      <div class="dt-tc-right">
        <div class="dt-tc-num">~$161,640</div>
        <div style="font-size:9px;color:var(--muted);">True annual cost — one human recruiter</div>
        <div class="dt-tc-vs">BlueLine: $18,000/yr · 365 days · 0 absences</div>
      </div>
    </div>
  </div>
</div>

<div class="gap"></div>

<!-- ═══════════════════════════════════════════ -->
<!-- SECTION B: AGENCY COST CALCULATOR          -->
<!-- ═══════════════════════════════════════════ -->
<div class="section" id="sec-calc">
  <div class="section-label" id="lbl-calc">Agency Cost Calculator — Cost Per Placement</div>
  <div class="cpp-grid">
    <div class="cpp-inputs">
      <div class="calc-group">
        <div class="calc-label">Number of recruiters doing outreach</div>
        <div class="calc-val-sm" id="cpRC">1</div>
        <input type="range" class="calc-slider" id="slRC" min="1" max="8" value="1" oninput="calcCPP()">
      </div>
      <div class="calc-group">
        <div class="calc-label">Annual cost per recruiter (salary + overhead)</div>
        <div class="calc-val-sm" id="cpCost">$62K</div>
        <input type="range" class="calc-slider" id="slCost" min="45000" max="110000" step="1000" value="62000" oninput="calcCPP()">
      </div>
      <div class="calc-group">
        <div class="calc-label">Current placements per recruiter / month</div>
        <div class="calc-val-sm" id="cpPl">8</div>
        <input type="range" class="calc-slider" id="slPl" min="2" max="25" value="8" oninput="calcCPP()">
      </div>
      <div class="calc-group">
        <div class="calc-label">BlueLine plan</div>
        <div class="tier-toggle">
          <div class="tier-btn selected" id="tStarter" onclick="selTier('starter')">Starter $800/mo</div>
          <div class="tier-btn" id="tPro" onclick="selTier('pro')">Professional $1,500/mo</div>
        </div>
      </div>
    </div>
    <div class="cpp-results">
      <div class="cpp-insight red">
        <div class="cpp-insight-num" style="color:var(--red);" id="rManualCPP">—</div>
        <div class="cpp-insight-label">Cost per placement — manual process</div>
        <div class="cpp-insight-sub">Total recruiter cost ÷ total monthly placements</div>
      </div>
      <div class="cpp-insight green">
        <div class="cpp-insight-num" style="color:var(--green);" id="rAICPP">—</div>
        <div class="cpp-insight-label">Cost per placement — with BlueLine</div>
        <div class="cpp-insight-sub">Same headcount, 45% more placements</div>
      </div>
      <div class="cpp-insight amber">
        <div class="cpp-insight-num" style="color:var(--amber);" id="rExtra">—</div>
        <div class="cpp-insight-label">Additional placements per month — same headcount</div>
        <div class="cpp-insight-sub">From reclaimed outreach time (stages 1–4)</div>
      </div>
      <div class="cpp-insight purple">
        <div class="cpp-insight-num" style="color:#c4b5fd;" id="rSaving">—</div>
        <div class="cpp-insight-label">Annual cost reduction (vs fully manual process)</div>
        <div class="cpp-insight-sub">Includes BlueLine subscription cost</div>
      </div>
      <div class="cpp-assumption">Assumption: BlueLine automates stages 1–4 (outreach, follow-up, ATS entry, reply handling), freeing ~45% of recruiter time for stages 5–6. Placement rate uplift: +25% conservative from faster response time alone. <span style="color:#334155;">(Source: HCI candidate conversion studies, 2023)</span></div>
    </div>
  </div>
</div>

<div class="gap"></div>

<!-- ═══════════════════════════════════════════ -->
<!-- CANDIDATE SOURCES                          -->
<!-- ═══════════════════════════════════════════ -->
<div class="section" id="sec-sources">
  <div class="section-label" id="lbl-sources">Candidate Sources</div>
  <div class="inputs-row">
    <div class="source-card" id="src-csv">
      <div class="icon">📋</div>
      <div class="title">CSV Lead List</div>
      <div class="detail">CONFIDENTIAL_candidates.csv<br>344+ pre-loaded leads<br>Role / Location / Phone</div>
    </div>
    <div class="source-card" id="src-indeed">
      <div class="icon">💼</div>
      <div class="title">Indeed Applicants</div>
      <div class="detail">Employer portal resumes<br>Manual download → Claude reads<br>Real emails only (no proxy)</div>
    </div>
    <div class="source-card" id="src-email">
      <div class="icon">📧</div>
      <div class="title">Inbound Email</div>
      <div class="detail">info@bluelinestaffing.com<br>Document submissions<br>Attachment analysis via Vision</div>
    </div>
  </div>
</div>

<div class="flow-track" id="flow1">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path id="arr1" d="M12 4v12M6 13l6 7 6-7" stroke="#252840" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</div>

<!-- MASTER DAILY AGENT -->
<div class="section" id="sec-engine">
  <div class="section-label" id="lbl-engine">Master Daily Agent</div>
  <div class="engine" id="engine-box">
    <div class="engine-title">⚙️ Master Daily Agent — Logical Recruitment Funnel</div>
    <div class="steps-grid">
      <div class="step s2" id="step1e">
        <div class="step-num">STEP 1</div>
        <div class="step-name">New Lead Intro</div>
        <div class="step-detail">30 new leads/day (150 catch-up max).<br>Full dedup: name + phone vs all live contacts.<br>Auto-detects license + NYC borough.<br>Marks processed on confirmed send only.</div>
      </div>
      <div class="step s3" id="step2e">
        <div class="step-num">STEP 2</div>
        <div class="step-name">SMS Reply Handler</div>
        <div class="step-detail">Scans all inbound messages.<br>INTEREST → Document checklist in &lt;10s.<br>STOP/OPT-OUT → Permanent block + rename.<br>Unknown → Human review queue.</div>
      </div>
      <div class="step s1" id="step3e">
        <div class="step-num">STEP 3</div>
        <div class="step-name">Re-engage Stalled</div>
        <div class="step-detail">Targets contacts silent 96+ hours.<br>Reads SMS + email history before sending.<br>Claude decides: SKIP or personalised SMS.<br>Never sends if mid-process.</div>
      </div>
      <div class="step s0" id="step4e">
        <div class="step-num">STEP 4</div>
        <div class="step-name">Document Review</div>
        <div class="step-detail">Claude Vision reads all inbound attachments.<br>Checks: License · Physical · Titers · BLS · TB<br>Validates NYS date windows.<br>→ Drafts reply with ✓/✗ checklist. Never auto-sends.</div>
      </div>
    </div>
  </div>
</div>

<div class="flow-track" id="flow2">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path id="arr2" d="M12 4v12M6 13l6 7 6-7" stroke="#252840" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</div>

<!-- INTELLIGENCE LAYER -->
<div class="section" id="sec-intel">
  <div class="section-label" id="lbl-intel">Intelligence Layer</div>
  <div class="logic-row">
    <div class="logic-card" id="intel-upgrade">
      <div class="lc-title">🧠 Upgrade 1 — Context Guard</div>
      <div class="lc-body">Before every re-engagement SMS:<br>1. Pull 4-day Quo SMS history<br>2. Pull 4-day Gmail thread history<br>3. Claude (Haiku) decides:<br>&nbsp;&nbsp;<span class="badge badge-red">SKIP</span> mid-process / recent<br>&nbsp;&nbsp;<span class="badge badge-green">SEND</span> contextual follow-up</div>
    </div>
    <div class="logic-card" id="intel-dedup">
      <div class="lc-title">🔍 Dedup Engine</div>
      <div class="lc-body">Three-pass check before every create:<br><span class="badge badge-blue">Phone</span> normalised E.164 match<br><span class="badge badge-blue">Name</span> normalised full name match<br><span class="badge badge-blue">First</span> first token match<br>No false contacts. No double-sends.</div>
    </div>
    <div class="logic-card" id="intel-class">
      <div class="lc-title">📍 Auto-Classification</div>
      <div class="lc-body"><span class="badge badge-amber">License</span> RN · LPN · CNA from CSV Role column<br><span class="badge badge-amber">Borough</span> detect from address + ZIP codes<br>Stored in Quo lastName as "RN, Brooklyn"<br>Drives personalisation at every step.</div>
    </div>
    <div class="logic-card" id="intel-comply">
      <div class="lc-title">🛡️ Compliance Layer</div>
      <div class="lc-body"><span class="badge badge-red">BLOCKED</span> number registry (hardcoded)<br>Permanent opt-out file (TCPA safe)<br>Contact renamed: DO NOT MESSAGE<br>State files survive restarts.</div>
    </div>
  </div>
</div>

<div class="flow-track" id="flow3">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path id="arr3" d="M12 4v12M6 13l6 7 6-7" stroke="#252840" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</div>

<!-- OUTPUTS -->
<div class="section" id="sec-outputs">
  <div class="section-label" id="lbl-outputs">Outputs</div>
  <div class="outputs-row">
    <div class="out-card" id="out-sms"><div class="out-icon">💬</div><div class="out-title">Outbound SMS</div><div class="out-detail">Via OpenPhone API<br>+15512506678 → Dylan</div></div>
    <div class="out-card" id="out-drafts"><div class="out-icon">📝</div><div class="out-title">Gmail Drafts</div><div class="out-detail">Doc review replies<br>Aditya sends manually</div></div>
    <div class="out-card" id="out-review"><div class="out-icon">🚩</div><div class="out-title">Human Review Queue</div><div class="out-detail">Unrecognised replies<br>master_needs_human_review.txt</div></div>
    <div class="out-card" id="out-log"><div class="out-icon">📊</div><div class="out-title">Run Log CSV</div><div class="out-detail">Per-run action log<br>Timestamped · Auditable</div></div>
  </div>
</div>

<div class="gap"></div>

<!-- METRICS -->
<div class="section" id="sec-metrics">
  <div class="section-label" id="lbl-metrics">Pipeline Stats</div>
  <div class="metrics">
    <div class="metric" id="m1"><div class="metric-num">344+</div><div class="metric-label">Processed Contacts</div></div>
    <div class="metric" id="m2"><div class="metric-num">41</div><div class="metric-label">Active Convos (7d)</div></div>
    <div class="metric" id="m3"><div class="metric-num">30/day</div><div class="metric-label">New Lead Rate</div></div>
    <div class="metric" id="m4"><div class="metric-num">5</div><div class="metric-label">NYC Boroughs</div></div>
    <div class="metric" id="m5"><div class="metric-num">13</div><div class="metric-label">Bugs Fixed (v2.1)</div></div>
    <div class="metric" id="m6"><div class="metric-num">0</div><div class="metric-label">Auto-sends (email)</div></div>
  </div>
</div>

<div class="gap"></div>

<!-- COMPLIANCE -->
<div class="section" id="sec-comply">
  <div class="section-label" id="lbl-comply">Compliance &amp; Safety</div>
  <div class="compliance" id="comply-box">
    <div><div class="ct">TCPA</div><div class="ci">Permanent opt-out file · Never re-contacts<br>Blocked numbers registry hardcoded</div></div>
    <div><div class="ct">Data</div><div class="ci">.env + CSV + OAuth token never committed<br>No PII in logs beyond name + phone</div></div>
    <div><div class="ct">Human-in-loop</div><div class="ci">All email replies are drafts only<br>Unrecognised SMS → review queue</div></div>
    <div><div class="ct">Audit trail</div><div class="ci">Run log CSV per execution<br>State files survive between runs</div></div>
  </div>
</div>

<script>
/* ═══ CALCULATOR ═══ */
let arcTier = 'starter';
function selTier(t){
  arcTier=t;
  document.getElementById('tStarter').classList.toggle('selected',t==='starter');
  document.getElementById('tPro').classList.toggle('selected',t==='pro');
  calcCPP();
}
function calcCPP(){
  const rc=+document.getElementById('slRC').value;
  const cost=+document.getElementById('slCost').value;
  const pl=+document.getElementById('slPl').value;
  const blMo=arcTier==='starter'?800:1500;
  document.getElementById('cpRC').textContent=rc;
  document.getElementById('cpCost').textContent='$'+Math.round(cost/1000)+'K';
  document.getElementById('cpPl').textContent=pl;
  const totalRecCost=rc*cost;
  const totalPl=rc*pl;
  const manualCPP=Math.round(totalRecCost/totalPl/12);
  const aiPl=Math.round(totalPl*1.45);
  const aiTotalCost=totalRecCost+blMo*12;
  const aiCPP=Math.round(aiTotalCost/aiPl/12);
  const extra=aiPl-totalPl;
  const saving=Math.round((manualCPP-aiCPP)*aiPl*12);
  document.getElementById('rManualCPP').textContent='$'+manualCPP;
  document.getElementById('rAICPP').textContent='$'+aiCPP;
  document.getElementById('rExtra').textContent='+'+extra+'/mo';
  document.getElementById('rSaving').textContent='$'+Math.round(saving/1000)+'K/yr';
}
calcCPP();

/* ═══ ANIMATION ENGINE ═══ */
let playing=false;
let currentIdx=-1;
let progressRaf=null;
let timers=[];

const synth=window.speechSynthesis;

const SEGMENTS=[
  {nar:"BlueLine Staffing AI Agent — version 2.1. Here's the full pipeline, end to end.",label:"Intro",
   anim:()=>{clearAll();}},
  {nar:"Here's the problem. A healthcare recruiter spends twelve to twenty hours of manual work to place a single nurse. Six stages. Thirty-six to forty-nine days end to end. BlueLine compresses the first four stages to zero.",label:"Recruitment Journey",
   anim:()=>{
     zoomSection('sec-journey');lightLabel('lbl-journey');
     ['jstg1','jstg2','jstg3','jstg4','jstg5','jstg6'].forEach((id,i)=>setTimeout(()=>lit(id),i*400));
   }},
  {nar:"Here's the number that's never in the proposal. The average US recruiter is out of the office thirty-seven days per year. That's fourteen percent of the work year paid for with zero output, and eleven hundred candidate contacts that never happen. Ninety-nine thousand dollars in missed gross margin. Every year. BlueLine runs three hundred and sixty-five days. Zero sick days. Zero vacation. Zero holidays.",label:"Recruiter Downtime",
   anim:()=>{
     zoomSection('sec-downtime');lightLabel('lbl-downtime');
   }},
  {nar:"The Agency Cost Calculator. Dial in your recruiter count, their fully-loaded cost, and your current placement rate. Add BlueLine and that same recruiter places forty-five percent more — your cost per placement drops, and the extra placements pay for the system many times over.",label:"Cost Calculator",
   anim:()=>{
     zoomSection('sec-calc');lightLabel('lbl-calc');
   }},
  {nar:"Three candidate sources feed the system every day. A CSV lead list with over three hundred candidates. Resumes pulled from Indeed. And inbound emails with attached documents.",label:"Candidate Sources",
   anim:()=>{
     zoomSection('sec-sources');lightLabel('lbl-sources');
     ['src-csv','src-indeed','src-email'].forEach((id,i)=>setTimeout(()=>lit(id),i*350));
   }},
  {nar:"Candidates flow into the Master Daily Agent.",label:"Flow → Agent",
   anim:()=>{
     zoomSections(['sec-sources','sec-engine']);
     animateArrow('flow1','#4f6ef7');
   }},
  {nar:"Step one: New Lead Intro. Thirty fresh candidates every morning — one hundred and fifty on catch-up weeks. Every contact cross-checked against all live records first. Zero duplicates. Borough and license-aware from the first message.",label:"Step 1 — New Leads",
   anim:()=>{
     zoomSection('sec-engine');lightLabel('lbl-engine');lit('engine-box');lit('step1e');
   }},
  {nar:"Step two: SMS Reply Handler. Candidates respond and the system acts instantly — YES gets the full document checklist in under ten seconds. STOP triggers a permanent block and contact rename. Unclear replies go to the human review queue with full context.",label:"Step 2 — SMS",
   anim:()=>{
     zoomSection('sec-engine');unlit('step1e');lit('engine-box');lit('step2e');
   }},
  {nar:"Step three: Re-engage Stalled contacts. Any candidate silent for four or more days gets a personalised follow-up — but only after the system reads their last four days of SMS and email history. If they're mid-process, it skips entirely.",label:"Step 3 — Re-engage",
   anim:()=>{
     zoomSection('sec-engine');unlit('step2e');lit('engine-box');lit('step3e');
   }},
  {nar:"Step four: Document Review. When a candidate submits credentials, Claude Vision reads every attachment — nursing license, physical, titers, TB, BLS, I-9 — validates all New York State date windows, and drafts a compliant checklist reply. Waiting in your inbox before 8 AM.",label:"Step 4 — Doc Review",
   anim:()=>{
     zoomSection('sec-engine');unlit('step3e');lit('engine-box');lit('step4e');
   }},
  {nar:"Every message passes through the Intelligence Layer before it goes out.",label:"Flow → Intelligence",
   anim:()=>{
     zoomSections(['sec-engine','sec-intel']);
     animateArrow('flow2','#7c3aed');
   }},
  {nar:"Upgrade One is the Context Guard — reads four days of SMS and email history before every re-engagement message. Claude decides: send something relevant, or skip entirely.",label:"Context Guard",
   anim:()=>{
     zoomSection('sec-intel');lightLabel('lbl-intel');lit('intel-upgrade');
   }},
  {nar:"The Dedup Engine runs three passes — phone number, full name, and first name — against every existing contact before creating anything new. No false contacts. No double sends.",label:"Dedup Engine",
   anim:()=>{
     zoomSection('sec-intel');unlit('intel-upgrade');lit('intel-dedup');
   }},
  {nar:"Auto-Classification reads the CSV Role column and candidate address to detect license type and NYC borough. That data drives personalisation at every step.",label:"Auto-Classification",
   anim:()=>{
     zoomSection('sec-intel');unlit('intel-dedup');lit('intel-class');
   }},
  {nar:"The Compliance Layer enforces a permanent blocked number registry. Opt-outs survive restarts, re-imports, and manual errors. Once in, there is no workflow that gets a number back out.",label:"Compliance Layer",
   anim:()=>{
     zoomSection('sec-intel');unlit('intel-class');lit('intel-comply');
   }},
  {nar:"Four clean outputs come out the other side.",label:"Flow → Outputs",
   anim:()=>{
     zoomSections(['sec-intel','sec-outputs']);
     animateArrow('flow3','#34d399');
   }},
  {nar:"Outbound SMS through your agency's SMS platform under your recruiter persona. Email draft replies that your team reviews before sending — nothing goes automatically. A human review queue for anything unrecognised. And a timestamped CSV log of every action the system took.",label:"Outputs",
   anim:()=>{
     zoomSection('sec-outputs');lightLabel('lbl-outputs');
     ['out-sms','out-drafts','out-review','out-log'].forEach((id,i)=>setTimeout(()=>lit(id),i*350));
   }},
  {nar:"Three hundred and forty-four candidates processed. Forty-one active conversations this week. Thirty new contacts every morning. Five boroughs covered. Thirteen bugs fixed in version 2.1. Zero emails sent without a human reviewing them first. That's the system.",label:"Stats & Compliance",
   anim:()=>{
     zoomSections(['sec-metrics','sec-comply']);
     lightLabel('lbl-metrics');lightLabel('lbl-comply');lit('comply-box');
     ['m1','m2','m3','m4','m5','m6'].forEach((id,i)=>setTimeout(()=>lit(id),i*150));
   }},
  {nar:"BlueLine Staffing AI Agent. Version 2.1. Running live.",label:"Done",
   anim:()=>{clearAll();}},
];

const ALL_SECS=['sec-journey','sec-downtime','sec-calc','sec-sources','sec-engine','sec-intel','sec-outputs','sec-metrics','sec-comply'];
function lit(id){document.getElementById(id)?.classList.add('lit');}
function unlit(id){document.getElementById(id)?.classList.remove('lit');}
function lightLabel(id){document.getElementById(id)?.classList.add('lit');}
function zoomSection(activeId){
  ALL_SECS.forEach(id=>{
    const el=document.getElementById(id);if(!el)return;
    el.classList.remove('dimmed','active-zoom');
    if(id===activeId){el.classList.add('active-zoom');el.scrollIntoView({behavior:'smooth',block:'center'});}
    else{el.classList.add('dimmed');}
  });
}
function zoomSections(activeIds){
  ALL_SECS.forEach(id=>{
    const el=document.getElementById(id);if(!el)return;
    el.classList.remove('dimmed','active-zoom');
    if(activeIds.includes(id)){el.classList.add('active-zoom');}
    else{el.classList.add('dimmed');}
  });
  const first=document.getElementById(activeIds[0]);
  if(first)first.scrollIntoView({behavior:'smooth',block:'center'});
}
function dimAll(){
  ALL_SECS.forEach(id=>{
    const el=document.getElementById(id);if(!el)return;
    el.classList.add('dimmed');el.classList.remove('active-zoom');
  });
  document.querySelectorAll('.lit').forEach(el=>el.classList.remove('lit'));
}
function clearAll(){
  ALL_SECS.forEach(id=>{
    const el=document.getElementById(id);if(!el)return;
    el.classList.remove('dimmed','active-zoom');
  });
  document.querySelectorAll('.lit').forEach(el=>el.classList.remove('lit'));
}
function lightSection(id){
  document.getElementById(id)?.classList.remove('dimmed');
}
function animateArrow(trackId,color){
  const track=document.getElementById(trackId);if(!track)return;
  const path=track.querySelector('path');if(path)path.setAttribute('stroke',color);
  for(let i=0;i<6;i++){
    setTimeout(()=>{
      const p=document.createElement('div');p.className='particle';
      p.style.background=color;track.appendChild(p);
      setTimeout(()=>p.remove(),900);
    },i*150);
  }
}

function setNar(text){
  document.getElementById('narText').textContent=text;
  document.getElementById('waveEl').classList.remove('hidden');
}
function clearNar(){
  document.getElementById('waveEl').classList.add('hidden');
  document.getElementById('narText').textContent='Press Play to walk through the pipeline with audio narration.';
}

/* Web Speech API narration */
function speak(text,onEnd){
  synth.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.rate=0.92;u.pitch=1.0;u.volume=1;
  const voices=synth.getVoices();
  const preferred=voices.find(v=>v.name.includes('Samantha')||v.name.includes('Google US English')||v.lang==='en-US');
  if(preferred)u.voice=preferred;
  u.onend=()=>{if(onEnd)onEnd();};
  u.onerror=()=>{if(onEnd)onEnd();};
  synth.speak(u);
}

function playSegment(idx){
  if(!playing||idx>=SEGMENTS.length){finish();return;}
  currentIdx=idx;
  SEGMENTS[idx].anim();
  setNar(SEGMENTS[idx].nar);
  document.getElementById('stepLabel').textContent=SEGMENTS[idx].label;
  speak(SEGMENTS[idx].nar,()=>{
    if(playing)playSegment(idx+1);
  });
  updateProgress(idx);
}

function updateProgress(idx){
  const pct=Math.round((idx/SEGMENTS.length)*100);
  document.getElementById('progressBar').style.width=pct+'%';
}

function finish(){
  playing=false;currentIdx=-1;
  clearNar();clearAll();
  document.getElementById('progressBar').style.width='100%';
  document.getElementById('stepLabel').textContent='Complete';
  document.getElementById('playBtn').textContent='▶ Play';
  document.getElementById('playBtn').classList.remove('active');
}

function togglePlay(){
  if(playing){
    playing=false;synth.cancel();
    document.getElementById('playBtn').textContent='▶ Play';
    document.getElementById('playBtn').classList.remove('active');
  }else{restart();}
}

function restart(){
  playing=false;synth.cancel();
  clearAll();
  document.getElementById('progressBar').style.width='0%';
  document.getElementById('stepLabel').textContent='Starting…';
  document.getElementById('playBtn').textContent='⏸ Pause';
  document.getElementById('playBtn').classList.add('active');
  playing=true;
  setTimeout(()=>playSegment(0),100);
}

if(synth.onvoiceschanged!==undefined)synth.onvoiceschanged=()=>synth.getVoices();
synth.getVoices();
</script>
</body>
</html>"""

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(HTML)

size_kb = os.path.getsize(OUT) // 1024
print(f"Written: {OUT}")
print(f"Size: {size_kb} KB")
print("Next: run build_arch_audio.py to generate and embed ElevenLabs narration")
