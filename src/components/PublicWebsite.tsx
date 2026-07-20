import React, { useState } from 'react';
import { Sparkles, Calendar, ArrowRight, CheckCircle2, ShieldAlert, BadgeDollarSign, ShieldCheck } from 'lucide-react';

interface PublicWebsiteProps {
  onEnterDashboard: () => void;
  onEnterClientPortal: () => void;
}

export default function PublicWebsite({ onEnterDashboard, onEnterClientPortal }: PublicWebsiteProps) {
  const [nurses, setNurses] = useState(30);
  const [hours, setHours] = useState(15);
  
  // Dylan saves ~83% of intake time. At an average coordinator wage of $28/hr
  const monthlySavings = Math.round(hours * 4.33 * 0.83 * 28 + (nurses * 15)); 
  const annualSavings = monthlySavings * 12;

  return (
    <div className="bg-[#04080E] text-white font-sans selection:bg-[#00BAC8]/30 overflow-x-hidden" id="home">
      {/* Navigation */}
      <header className="sticky top-0 z-50 bg-[#04080E]/85 backdrop-blur-md border-b border-white/8">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-[#00BAC8]/10 border border-[#00BAC8] flex items-center justify-center font-bold text-lg text-[#00BAC8] font-display">D</div>
            <span className="font-bold text-lg tracking-wider font-display">DYLAN <span className="text-[#00BAC8]">FOR HIRE</span></span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm text-gray-400">
            <a href="#problem" className="hover:text-white transition-colors">The Problem</a>
            <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
            <a href="#roi" className="hover:text-white transition-colors">Savings Calculator</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
            <button 
              onClick={onEnterClientPortal}
              className="hover:text-[#00BAC8] text-gray-400 font-semibold cursor-pointer transition-colors"
            >
              Facility Portal
            </button>
          </nav>
          <div className="flex items-center gap-3">
            <button 
              onClick={onEnterClientPortal}
              className="px-3 py-1.5 text-xs text-gray-400 hover:text-white hover:bg-white/5 border border-white/10 rounded-md transition-all"
            >
              Client Login
            </button>
            <button 
              id="goto-dashboard-btn"
              onClick={onEnterDashboard}
              className="px-4 py-2 text-xs font-semibold bg-[#00BAC8]/10 border border-[#00BAC8]/40 hover:border-[#00BAC8] text-[#00BAC8] rounded-md transition-all flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 animate-pulse" /> Launch Back Office
            </button>
            <a 
              href="https://calendly.com/adi-dylan/dylan-demo" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hidden sm:inline-flex px-4 py-2 text-xs font-bold bg-[#00BAC8] text-[#04080E] rounded-md hover:opacity-90 transition-all shadow-lg shadow-[#00BAC8]/20"
            >
              Book a Demo
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-24 pb-20 text-center bg-radial from-[#0d1620] via-[#04080E] to-[#04080E] border-b border-white/5">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none" />
        <div className="max-w-4xl mx-auto px-6 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#00BAC8]/10 border border-[#00BAC8]/30 text-xs font-bold text-[#00BAC8] tracking-widest uppercase mb-6 font-display">
            Healthcare Staffing, Automated
          </div>
          <h1 className="text-4xl sm:text-6xl font-bold tracking-tight leading-tight mb-6 font-display">
            Your Nurse Staffing Agency. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00BAC8] to-[#00E676]">Fully Automated.</span>
          </h1>
          <p className="text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed font-sans">
            Dylan runs your candidate intake, credential audits, and shift matching — so you place more nurses without adding headcount. Proven at BlueLine Staffing NYC.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a 
              href="https://calendly.com/adi-dylan/dylan-demo" 
              target="_blank" 
              rel="noopener noreferrer"
              className="px-8 py-4 bg-[#00BAC8] text-[#04080E] font-bold rounded-lg hover:opacity-90 transition-all shadow-xl shadow-[#00BAC8]/10 flex items-center gap-2"
            >
              Book Your Free 30-Min Demo <ArrowRight className="w-4 h-4" />
            </a>
            <button 
              onClick={onEnterDashboard}
              className="px-8 py-4 bg-white/5 border border-white/10 hover:bg-white/10 font-bold rounded-lg transition-all text-sm flex items-center gap-2"
            >
              Explore Back-Office Simulation
            </button>
          </div>
          <div className="text-xs text-gray-500 mt-4">30 minutes. No pressure. See exactly how it works.</div>

          {/* KPI Stat Strip */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 mt-16 max-w-3xl mx-auto border-t border-white/10 pt-10">
            <div className="text-center">
              <div className="text-3xl font-extrabold text-[#00E676] font-display">83%</div>
              <div className="text-xs text-gray-400 mt-1.5">Faster candidate intake</div>
            </div>
            <div className="text-center border-y sm:border-y-0 sm:border-x border-white/10 py-4 sm:py-0">
              <div className="text-3xl font-extrabold text-[#00E676] font-display">&lt;4 min</div>
              <div className="text-xs text-gray-400 mt-1.5">Candidate to placement alert</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-extrabold text-[#00E676] font-display">11-pt</div>
              <div className="text-xs text-gray-400 mt-1.5">Credential audit, zero human review</div>
            </div>
          </div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="py-20 bg-[#080D15]" id="problem">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <div className="text-[#00BAC8] text-xs font-bold uppercase tracking-widest mb-3 font-display">The Problem</div>
            <h2 className="text-3xl sm:text-4xl font-bold font-display">Your Agency Is Leaking Time &amp; Revenue</h2>
            <p className="text-gray-400 mt-3 text-sm sm:text-base">Every hour spent on manual intake and spreadsheets is an hour not spent placing nurses.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 bg-[#0B121C] border border-white/5 border-t-2 border-t-[#F04040] rounded-xl">
              <div className="w-10 h-10 rounded-lg bg-[#F04040]/10 flex items-center justify-center text-[#F04040] mb-6">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold mb-3 font-display">Manual Intake Chaos</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Candidates apply by text, email, and job boards. Someone has to chase, sort, verify, and re-enter details manually into multiple systems.
              </p>
            </div>

            <div className="p-8 bg-[#0B121C] border border-white/5 border-t-2 border-t-[#F04040] rounded-xl">
              <div className="w-10 h-10 rounded-lg bg-[#F04040]/10 flex items-center justify-center text-[#F04040] mb-6">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold mb-3 font-display">Credential Nightmares</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Licenses, BLS cards, TB screens, and tax documents tracked across sprawling Excel tabs. Easily missed until a facility catches a compliance error.
              </p>
            </div>

            <div className="p-8 bg-[#0B121C] border border-white/5 border-t-2 border-t-[#F04040] rounded-xl">
              <div className="w-10 h-10 rounded-lg bg-[#F04040]/10 flex items-center justify-center text-[#F04040] mb-6">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold mb-3 font-display">Slow Matching Lag</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                By the time your staff reconciles spreadsheet schedules, filters compliant candidates, and texts them, faster-moving competitors have placed their nurses.
              </p>
            </div>
          </div>
          
          <div className="text-center mt-12">
            <p className="text-lg font-bold font-display text-gray-300">
              "Every hour spent on paperwork is <span className="text-[#F04040]">an hour not spent placing nurses.</span>"
            </p>
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="py-20" id="how-it-works">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <div className="text-[#00BAC8] text-xs font-bold uppercase tracking-widest mb-3 font-display">The Solution</div>
            <h2 className="text-3xl sm:text-4xl font-bold font-display">Dylan Runs Your Back Office</h2>
            <p className="text-gray-400 mt-3 text-sm sm:text-base">One seamless, automated flow from first candidate touchpoint to a filled shift.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
            {[
              { num: "01", title: "Apply", desc: "Web, SMS, or email — capture starts the moment they reach out." },
              { num: "02", title: "Capture", desc: "Applicant info, contact, and preferences processed automatically into CRM." },
              { num: "03", title: "Audit", desc: "11-point credential check verified instantly via Dylan Vision. No human review." },
              { num: "04", title: "Match", desc: "Best-fit candidates paired by role, borough, and schedule in seconds." },
              { num: "05", title: "Alert", desc: "Dispatches automated shifts and reblasts alerts. Verified in <4 mins." }
            ].map((step, i) => (
              <div key={i} className="p-6 bg-[#0B121C] border border-white/5 border-t-2 border-t-[#00BAC8] rounded-xl relative">
                <div className="text-xs font-bold text-[#00BAC8] mb-3 font-mono">STEP {step.num}</div>
                <h4 className="text-base font-bold mb-2 font-display">{step.title}</h4>
                <p className="text-gray-400 text-xs leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>

          <div className="mt-12 p-8 bg-[#0B121C] border border-white/8 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6 max-w-5xl mx-auto">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-[#00BAC8]/10 border border-[#00BAC8] flex items-center justify-center text-[#00BAC8] shrink-0">
                <Calendar className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold font-display">Want to see it live with your own agency setup?</h4>
                <p className="text-xs text-gray-400 mt-1">Book a free 30-minute workspace session with us.</p>
              </div>
            </div>
            <a 
              href="https://calendly.com/adi-dylan/dylan-demo" 
              target="_blank" 
              rel="noopener noreferrer"
              className="px-6 py-3 bg-[#00BAC8] text-[#04080E] font-bold text-xs rounded-lg hover:opacity-90 transition-all shrink-0"
            >
              Schedule Free Workspace Session
            </a>
          </div>
        </div>
      </section>

      {/* Savings / ROI Calculator */}
      <section className="py-20 bg-[#080D15] border-t border-b border-white/5" id="roi">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <div className="text-[#00BAC8] text-xs font-bold uppercase tracking-widest mb-3 font-display">ROI Calculator</div>
            <h2 className="text-3xl font-bold font-display">Calculate Your Agency Savings</h2>
            <p className="text-gray-400 mt-2 text-sm">See how much coordinator overhead and placement leakage you can eliminate.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center bg-[#0B121C] border border-white/5 p-8 sm:p-12 rounded-2xl shadow-2xl shadow-black/40">
            {/* Input sliders */}
            <div className="space-y-8">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-300 font-medium">Nurses in Pool</span>
                  <span className="text-[#00BAC8] font-bold font-mono">{nurses} active</span>
                </div>
                <input 
                  type="range" 
                  min="5" 
                  max="150" 
                  value={nurses} 
                  onChange={(e) => setNurses(Number(e.target.value))}
                  className="w-full accent-[#00BAC8] bg-[#04080E] h-2 rounded-lg cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-gray-500 mt-1">
                  <span>5 Nurses</span>
                  <span>150 Nurses</span>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-300 font-medium">Intake &amp; Audit Hours/Week</span>
                  <span className="text-[#00BAC8] font-bold font-mono">{hours} hrs/week</span>
                </div>
                <input 
                  type="range" 
                  min="2" 
                  max="60" 
                  value={hours} 
                  onChange={(e) => setHours(Number(e.target.value))}
                  className="w-full accent-[#00BAC8] bg-[#04080E] h-2 rounded-lg cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-gray-500 mt-1">
                  <span>2 hours</span>
                  <span>60 hours</span>
                </div>
              </div>

              <div className="p-4 bg-[#04080E]/40 rounded-lg border border-white/5 text-xs text-gray-400">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-[#00E676] shrink-0 mt-0.5" />
                  <span>Calculated based on <strong>83% time reduction</strong> in document review and automated messaging workflows.</span>
                </div>
              </div>
            </div>

            {/* Results display */}
            <div className="p-8 bg-[#04080E] border border-[#00BAC8]/20 rounded-xl text-center space-y-6">
              <div>
                <span className="text-xs uppercase tracking-widest text-gray-400 font-medium block mb-1">Estimated Monthly Savings</span>
                <span className="text-4xl sm:text-5xl font-extrabold text-[#00E676] tracking-tight font-display">
                  ${monthlySavings.toLocaleString()}
                </span>
              </div>

              <div className="border-t border-white/5 pt-4">
                <span className="text-xs uppercase tracking-widest text-gray-400 font-medium block mb-1">Annual Resource Savings</span>
                <span className="text-xl font-bold text-[#00BAC8] font-display">
                  ${annualSavings.toLocaleString()} / year
                </span>
              </div>

              <button 
                onClick={onEnterDashboard}
                className="w-full py-3 bg-[#00BAC8]/10 border border-[#00BAC8] text-[#00BAC8] hover:bg-[#00BAC8] hover:text-[#04080E] font-bold text-xs rounded-lg transition-all flex items-center justify-center gap-1.5"
              >
                See Dylan Run the Math <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Proven At BlueLine Section */}
      <section className="py-20" id="proof">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <div className="text-[#00BAC8] text-xs font-bold uppercase tracking-widest mb-3 font-display">Case Study</div>
            <h2 className="text-3xl sm:text-4xl font-bold font-display">Proven At BlueLine Staffing NYC</h2>
            <p className="text-gray-400 mt-3 text-sm">Dylan isn't theoretical — it manages real operations, billing, and credentials every single day.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
            <div className="p-6 bg-[#0B121C] border border-white/5 border-t-4 border-t-[#00E676] rounded-xl text-center">
              <div className="text-4xl font-bold text-[#00E676] mb-2 font-display">37</div>
              <div className="text-xs text-gray-400 leading-relaxed font-sans">Active Nurses Managed (22 CNA, 9 LPN, 6 RN)</div>
            </div>
            <div className="p-6 bg-[#0B121C] border border-white/5 border-t-4 border-t-[#00E676] rounded-xl text-center">
              <div className="text-4xl font-bold text-[#00E676] mb-2 font-display">83%</div>
              <div className="text-xs text-gray-400 leading-relaxed font-sans">Reduction in coordinator onboarding overhead</div>
            </div>
            <div className="p-6 bg-[#0B121C] border border-white/5 border-t-4 border-t-[#00E676] rounded-xl text-center">
              <div className="text-4xl font-bold text-[#00E676] mb-2 font-display">&lt;4 min</div>
              <div className="text-xs text-gray-400 leading-relaxed font-sans">Time elapsed from document upload to compliant shift matching</div>
            </div>
            <div className="p-6 bg-[#0B121C] border border-white/5 border-t-4 border-t-[#00E676] rounded-xl text-center">
              <div className="text-4xl font-bold text-[#00E676] mb-2 font-display">1</div>
              <div className="text-xs text-gray-400 leading-relaxed font-sans">Staff member handles the volume that previously required 3</div>
            </div>
          </div>

          <div className="max-w-3xl mx-auto border-l-2 border-[#00BAC8] pl-6 md:pl-10 py-2">
            <p className="text-lg md:text-xl font-medium italic text-gray-200 leading-relaxed">
              "I built Dylan to run my own nurse staffing agency's back office — not as a sales pitch, but because I needed it. These are BlueLine's real numbers, not projections."
            </p>
            <div className="text-xs text-gray-400 font-bold uppercase mt-4 tracking-wider">
              — Aditya, Founder, Dylan for Hire · Operator, BlueLine Staffing NYC
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Table Section */}
      <section className="py-20 bg-[#080D15] border-t border-white/5" id="pricing">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <div className="text-[#00BAC8] text-xs font-bold uppercase tracking-widest mb-3 font-display">Pricing</div>
            <h2 className="text-3xl font-bold font-display">Simple Pricing. Real ROI.</h2>
            <p className="text-gray-400 mt-2 text-sm">Start automations simple or deploy custom-branded agent suites for your team.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch max-w-5xl mx-auto">
            {/* Tier 1 */}
            <div className="p-8 bg-[#0B121C] border border-white/5 rounded-2xl flex flex-col justify-between">
              <div>
                <span className="text-[#00BAC8] text-[10px] font-bold tracking-wider uppercase">DIY Template</span>
                <div className="text-3xl font-bold text-white mt-2 font-display">$497</div>
                <div className="text-xs text-gray-400 mt-1">One-time template setup</div>
                <ul className="text-xs text-gray-400 space-y-3.5 mt-8 border-t border-white/5 pt-6">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Complete standard scripts bundle</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Standard Google Apps integration</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Self-guided documentation checklist</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> No custom branding or active support</li>
                </ul>
              </div>
              <a 
                href="https://calendly.com/adi-dylan/dylan-demo" 
                target="_blank" 
                rel="noopener noreferrer"
                className="w-full text-center py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-bold text-xs rounded-lg mt-8 transition-all"
              >
                Book a Setup Call
              </a>
            </div>

            {/* Tier 2 */}
            <div className="p-8 bg-[#0B121C] border-2 border-[#EFB01F] rounded-2xl flex flex-col justify-between relative shadow-xl shadow-[#EFB01F]/5">
              <span className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-[#EFB01F] text-[#04080E] text-[10px] font-extrabold tracking-widest uppercase">MOST POPULAR</span>
              <div>
                <span className="text-[#00BAC8] text-[10px] font-bold tracking-wider uppercase">Pro Retainer</span>
                <div className="text-3xl font-bold text-white mt-2 font-display">$1,500 <span className="text-sm font-normal text-gray-400">+ $750/mo</span></div>
                <div className="text-xs text-gray-400 mt-1">Full-service active deployment</div>
                <ul className="text-xs text-gray-400 space-y-3.5 mt-8 border-t border-white/5 pt-6">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Full custom builds &amp; mapping in 10 days</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Interactive candidate pipelines &amp; portal</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> 11-point Dylan Vision Credential Auditor</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Continuous support, maintenance &amp; audits</li>
                </ul>
              </div>
              <a 
                href="https://calendly.com/adi-dylan/dylan-demo" 
                target="_blank" 
                rel="noopener noreferrer"
                className="w-full text-center py-3 bg-[#00BAC8] hover:bg-[#00BAC8]/90 text-[#04080E] font-bold text-xs rounded-lg mt-8 transition-all"
              >
                Book Your Demo
              </a>
            </div>

            {/* Tier 3 */}
            <div className="p-8 bg-[#0B121C] border border-white/5 rounded-2xl flex flex-col justify-between">
              <div>
                <span className="text-[#00BAC8] text-[10px] font-bold tracking-wider uppercase">Enterprise</span>
                <div className="text-3xl font-bold text-white mt-2 font-display">Custom</div>
                <div className="text-xs text-gray-400 mt-1">For multi-state agencies</div>
                <ul className="text-xs text-gray-400 space-y-3.5 mt-8 border-t border-white/5 pt-6">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Multi-state scheduling and directories</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Full white-label branding options</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Dedicated SLAs &amp; database routing</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Custom client-system database adapters</li>
                </ul>
              </div>
              <a 
                href="https://calendly.com/adi-dylan/dylan-demo" 
                target="_blank" 
                rel="noopener noreferrer"
                className="w-full text-center py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-bold text-xs rounded-lg mt-8 transition-all"
              >
                Talk to Enterprise Team
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24 text-center bg-radial from-[#0d1620] via-[#04080E] to-[#04080E] border-t border-white/5">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl sm:text-5xl font-bold mb-4 font-display">Your Agency. Automated in 10 Days.</h2>
          <p className="text-gray-400 text-sm sm:text-base max-w-xl mx-auto mb-10 leading-relaxed">
            Schedule a free 30-minute demonstration today. We will review your client roster and build a live-simulation plan.
          </p>
          <a 
            href="https://calendly.com/adi-dylan/dylan-demo" 
            target="_blank" 
            rel="noopener noreferrer"
            className="px-8 py-4 bg-[#00BAC8] text-[#04080E] font-bold rounded-lg hover:opacity-90 transition-all shadow-xl shadow-[#00BAC8]/20 inline-flex items-center gap-2"
          >
            Book Your Free 30-Min Demo
          </a>
          <div className="flex flex-wrap justify-center gap-4 mt-12 text-xs text-gray-500">
            <span className="px-3 py-1.5 rounded-full bg-white/5 border border-white/5">📞 551-250-6678</span>
            <span className="px-3 py-1.5 rounded-full bg-white/5 border border-white/5">🗓 Mon–Fri, 9am–6pm EST</span>
            <span className="px-3 py-1.5 rounded-full bg-white/5 border border-white/5">💬 30-Min Demo Call</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 text-center text-xs text-gray-500 border-t border-white/5 bg-[#04080E]">
        <div className="max-w-7xl mx-auto px-6">
          © 2026 Dylan for Hire. Built for nurse staffing agencies that want to grow without growing headcount.
        </div>
      </footer>
    </div>
  );
}
