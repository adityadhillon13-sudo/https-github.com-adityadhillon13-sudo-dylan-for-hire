import React, { useState, useEffect } from 'react';
import { Candidate, Shift, ReviewItem, LogEntry, SystemSettings } from './types';
import PublicWebsite from './components/PublicWebsite';
import ClientPortal from './components/ClientPortal';
import CandidatePipeline from './components/CandidatePipeline';
import CredentialAudit from './components/CredentialAudit';
import ShiftMatching from './components/ShiftMatching';
import ReviewQueue from './components/ReviewQueue';
import LiveConsole from './components/LiveConsole';
import SettingsPanel from './components/SettingsPanel';
import MasterDashboard from './components/MasterDashboard';
import LiveDashboard from './components/LiveDashboard';
import LoginScreen from './components/LoginScreen';

import { 
  Users, ShieldCheck, Calendar, MessageSquare, Terminal, Settings, 
  ArrowLeft, Compass, Sparkles, MessageCircle, Mail, Phone, RefreshCw, AlertCircle,
  LayoutDashboard, Radio, LogOut
} from 'lucide-react';

type ScreenMode = 'landing' | 'login' | 'backoffice' | 'client-portal';
type BackofficeTab = 'dashboard' | 'live' | 'pipeline' | 'audit' | 'shifts' | 'reviews' | 'console' | 'settings';

export default function App() {
  const [mode, setMode] = useState<ScreenMode>('landing');
  const [tab, setTab] = useState<BackofficeTab>('dashboard');
  const [userRole, setUserRole] = useState<'admin' | 'client' | null>(null);
  const [defaultLoginRole, setDefaultLoginRole] = useState<'admin' | 'client'>('admin');
  
  // App States
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [reviewQueue, setReviewQueue] = useState<ReviewItem[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [blacklist, setBlacklist] = useState<string[]>([]);
  
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(false);

  // Inbound Simulation Widget States
  const [simCandidateId, setSimCandidateId] = useState('');
  const [simChannel, setSimChannel] = useState<'SMS' | 'Email'>('SMS');
  const [simMessageText, setSimMessageText] = useState('');
  const [simulating, setSimulating] = useState(false);
  const [simResult, setSimResult] = useState<string | null>(null);

  // Sync API Data
  const fetchData = async () => {
    try {
      const [candRes, shiftRes, revRes, logRes, setRes, blackRes] = await Promise.all([
        fetch('/api/candidates'),
        fetch('/api/shifts'),
        fetch('/api/review-queue'),
        fetch('/api/logs'),
        fetch('/api/settings'),
        fetch('/api/optouts')
      ]);

      if (candRes.ok) setCandidates(await candRes.json());
      if (shiftRes.ok) setShifts(await shiftRes.json());
      if (revRes.ok) setReviewQueue(await revRes.json());
      if (logRes.ok) setLogs(await logRes.json());
      if (setRes.ok) setSettings(await setRes.json());
      if (blackRes.ok) setBlacklist(await blackRes.json());
    } catch (err) {
      console.error("Error syncing with backend:", err);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh stats every 8 seconds for real-time simulation feel
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  // Post new candidate
  const handleAddCandidate = async (candData: any) => {
    const res = await fetch('/api/candidates', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(candData)
    });
    if (res.ok) {
      await fetchData();
    }
  };

  // Update candidate profile
  const handleUpdateCandidate = async (updatedCand: Candidate) => {
    const res = await fetch(`/api/candidates/${updatedCand.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedCand)
    });
    if (res.ok) {
      await fetchData();
      // Keep selected reference in sync
      if (selectedCandidate?.id === updatedCand.id) {
        setSelectedCandidate(updatedCand);
      }
    }
  };

  // Post shift
  const handleAddShift = async (shiftData: any) => {
    const res = await fetch('/api/shifts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(shiftData)
    });
    if (res.ok) {
      await fetchData();
    }
  };

  // Match shift to candidate
  const handleMatchShift = async (shiftId: string, candidateId: string) => {
    const res = await fetch(`/api/shifts/${shiftId}/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidateId })
    });
    if (res.ok) {
      await fetchData();
    }
  };

  // Approve response
  const handleApproveReview = async (id: string, updatedReply: string) => {
    const res = await fetch(`/api/review-queue/${id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ updatedReply })
    });
    if (res.ok) {
      await fetchData();
    }
  };

  // Reject response
  const handleRejectReview = async (id: string) => {
    const res = await fetch(`/api/review-queue/${id}/reject`, {
      method: 'POST'
    });
    if (res.ok) {
      await fetchData();
    }
  };

  // Trigger daily cron cycle
  const handleTriggerDailyCron = async () => {
    const res = await fetch('/api/actions/run-daily-cron', { method: 'POST' });
    if (res.ok) {
      await fetchData();
    }
  };

  // Clear log console
  const handleClearConsole = async () => {
    const res = await fetch('/api/logs/clear', { method: 'POST' });
    if (res.ok) {
      await fetchData();
    }
  };

  // Update system settings
  const handleUpdateSettings = async (newSettings: SystemSettings) => {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSettings)
    });
    if (res.ok) {
      setSettings(await res.json());
      await fetchData();
    }
  };

  // Add to permanent blacklist
  const handleAddBlacklist = async (phone: string) => {
    const res = await fetch('/api/optouts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    if (res.ok) {
      setBlacklist(await res.json());
      await fetchData();
    }
  };

  // Run inbound communication simulator
  const handleSimulateInbound = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!simCandidateId || !simMessageText) return;
    setSimulating(true);
    setSimResult(null);

    try {
      const res = await fetch('/api/actions/simulate-inbound', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidateId: simCandidateId,
          channel: simChannel,
          messageText: simMessageText
        })
      });

      const data = await res.json();
      if (res.ok) {
        setSimResult(data.optedOut 
          ? "Opt-out keyword detected! Candidate blacklisted immediately." 
          : data.needsReview 
            ? "Simulated! Message sent. Dylan generated a reply which has been sent to the approval station." 
            : "Simulated! Message sent. Dylan auto-routed the response successfully."
        );
        setSimMessageText('');
        await fetchData();
        // Redirect to reviews tab if review is required
        if (data.needsReview) {
          setTab('reviews');
        }
      } else {
        setSimResult("Simulation error occurred.");
      }
    } catch (err: any) {
      setSimResult("Error calling simulator: " + err.message);
    } finally {
      setSimulating(false);
    }
  };

  if (mode === 'landing') {
    return (
      <PublicWebsite 
        onEnterDashboard={() => {
          setDefaultLoginRole('admin');
          setMode('login');
        }} 
        onEnterClientPortal={() => {
          setDefaultLoginRole('client');
          setMode('login');
        }}
      />
    );
  }

  if (mode === 'login') {
    return (
      <LoginScreen 
        defaultRole={defaultLoginRole}
        onLogin={(role) => {
          setUserRole(role);
          setMode('backoffice');
          // Start clients on the master dashboard, admins on the master dashboard
          setTab('dashboard');
        }}
      />
    );
  }

  if (mode === 'client-portal') {
    return (
      <ClientPortal
        candidates={candidates}
        shifts={shifts}
        reviewItems={reviewQueue}
        onAddShift={handleAddShift}
        onBackToLanding={() => setMode('landing')}
      />
    );
  }

  return (
    <div className="min-h-screen bg-[#04080E] text-gray-100 flex flex-col font-sans selection:bg-[#00BAC8]/30">
      {/* Back Office Top Bar */}
      <header className="bg-[#080D15] border-b border-white/5 h-16 flex items-center justify-between px-6 shrink-0 sticky top-0 z-40">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setMode('landing')}
            className="flex items-center gap-1.5 px-3 py-1.5 border border-white/10 rounded-lg text-xs text-gray-400 hover:text-white hover:bg-white/5 transition-all"
          >
            <ArrowLeft className="w-4 h-4" /> Marketing Site
          </button>
          
          <div className="h-4 w-[1px] bg-white/10" />

          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded bg-[#00BAC8]/10 border border-[#00BAC8]/30 flex items-center justify-center font-bold text-[#00BAC8] text-sm">D</div>
            <span className="font-bold text-sm tracking-wide font-display hidden sm:inline-block">DYLAN BACK OFFICE <span className="text-[#00BAC8] text-xs font-mono">v3.0</span></span>
          </div>
        </div>

        {/* Sync/Refresh Status & Top Switcher */}
        <div className="flex items-center gap-4">
          {/* Active View Quick Switcher */}
          <div className="flex items-center gap-1 bg-[#04080E] border border-white/10 rounded-xl p-1 shrink-0">
            <span className="text-[9px] text-gray-500 uppercase tracking-widest font-mono font-bold px-2 hidden lg:inline">Active Context:</span>
            <button
              onClick={() => {
                setUserRole('admin');
                setTab('dashboard');
              }}
              className={`px-2.5 py-1 text-[9px] font-bold font-mono rounded-lg transition-all ${
                userRole === 'admin'
                  ? 'bg-[#00BAC8] text-[#04080E] shadow-lg shadow-[#00BAC8]/10'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              💼 DFH Operator
            </button>
            <button
              onClick={() => {
                setUserRole('client');
                setTab('live');
              }}
              className={`px-2.5 py-1 text-[9px] font-bold font-mono rounded-lg transition-all ${
                userRole === 'client'
                  ? 'bg-[#9C27B0] text-white shadow-lg shadow-[#9C27B0]/10'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              🏢 BlueLine Client
            </button>
          </div>

          <button 
            onClick={fetchData} 
            className="p-2 border border-white/10 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-all"
            title="Force Sync State"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>

          <a 
            href="https://calendly.com/adi-dylan/dylan-demo" 
            target="_blank" 
            rel="noopener noreferrer"
            className="px-3.5 py-1.5 text-xs font-bold bg-[#00BAC8] text-[#04080E] rounded-md hover:opacity-90 transition-all shadow shadow-[#00BAC8]/10 hidden sm:inline-block"
          >
            Schedule Onboarding
          </a>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Sidebar Navigation */}
        <aside className="w-full md:w-64 bg-[#080D15] md:border-r border-b md:border-b-0 border-white/5 p-4 flex flex-col justify-between shrink-0 gap-6">
          <div className="space-y-6">
            <div className="space-y-1.5">
              <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block pl-2 font-mono">AUTOMATION WORKDesk</span>
              <nav className="space-y-1">
                {[
                  { id: 'dashboard', label: 'Dylan Master Dashboard', icon: LayoutDashboard, badge: null, adminOnly: false },
                  { id: 'live', label: 'BlueLine Live Dashboard', icon: Radio, badge: 29, adminOnly: false },
                  { id: 'pipeline', label: 'Candidate Pipeline', icon: Users, badge: candidates.filter(c => !c.optedOut).length, adminOnly: false },
                  { id: 'audit', label: '11-pt Credential Audit', icon: ShieldCheck, badge: null, adminOnly: false },
                  { id: 'shifts', label: 'NYC Shift Matching', icon: Calendar, badge: shifts.filter(s => s.status === 'Open').length, adminOnly: false },
                  { id: 'reviews', label: 'HIL Approval Hub', icon: MessageSquare, badge: reviewQueue.filter(item => item.status === "Pending").length, adminOnly: false },
                  { id: 'console', label: 'Log Terminal Stream', icon: Terminal, badge: null, adminOnly: true },
                  { id: 'settings', label: 'System Settings', icon: Settings, badge: null, adminOnly: true }
                ].filter(item => !item.adminOnly || userRole === 'admin').map((item) => {
                  const Icon = item.icon;
                  const isActive = tab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        setTab(item.id as any);
                        if (item.id !== 'audit') setSelectedCandidate(null);
                      }}
                      className={`w-full flex items-center justify-between p-2.5 rounded-lg text-xs font-semibold transition-all ${
                        isActive 
                          ? 'bg-[#00BAC8]/10 text-[#00BAC8] border border-[#00BAC8]/20' 
                          : 'text-gray-400 hover:text-white hover:bg-white/2'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <Icon className="w-4 h-4 shrink-0" />
                        <span>{item.label}</span>
                      </div>
                      {item.badge !== null && item.badge > 0 && (
                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold font-mono ${
                          item.id === 'reviews' ? 'bg-[#F04040]/10 text-[#F04040]' : 'bg-[#00BAC8]/10 text-[#00BAC8]'
                        }`}>
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* Simulated Live Communication Box */}
            <div className="bg-[#04080E]/80 border border-white/5 rounded-xl p-4 space-y-3.5 shadow-inner">
              <div className="flex items-center gap-1.5 text-[10px] text-[#00BAC8] font-bold uppercase font-mono tracking-wider">
                <Compass className="w-4 h-4 text-[#00BAC8] animate-pulse" />
                <span>SMS/Email Simulator</span>
              </div>
              <p className="text-[10px] text-gray-500 leading-normal">
                Trigger simulated candidate inbound texts or emails to see Dylan's automated capture, blacklisting, and response systems in action.
              </p>

              <form onSubmit={handleSimulateInbound} className="space-y-2.5">
                <div>
                  <select
                    value={simCandidateId}
                    onChange={(e) => setSimCandidateId(e.target.value)}
                    required
                    className="w-full bg-[#080D15] border border-white/10 rounded-md p-1.5 text-[10px] text-white focus:outline-none"
                  >
                    <option value="">-- Choose Nurse --</option>
                    {candidates.filter(c => !c.optedOut).map(c => (
                      <option key={c.id} value={c.id}>{c.name} ({c.role})</option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center gap-1 bg-[#080D15] border border-white/10 rounded-md p-0.5">
                  {(['SMS', 'Email'] as const).map(ch => (
                    <button
                      key={ch}
                      type="button"
                      onClick={() => setSimChannel(ch)}
                      className={`flex-1 py-1 text-[9px] font-bold rounded uppercase ${
                        simChannel === ch ? 'bg-white/5 text-[#00BAC8]' : 'text-gray-500'
                      }`}
                    >
                      {ch}
                    </button>
                  ))}
                </div>

                <div>
                  <input
                    type="text"
                    required
                    placeholder="e.g. STOP or what pays?"
                    value={simMessageText}
                    onChange={(e) => setSimMessageText(e.target.value)}
                    className="w-full bg-[#080D15] border border-white/10 rounded-md p-1.5 text-[10px] text-white focus:outline-none focus:border-[#00BAC8]"
                  />
                </div>

                <button
                  type="submit"
                  disabled={simulating || !simCandidateId}
                  className="w-full py-1.5 bg-[#00BAC8]/10 hover:bg-[#00BAC8] border border-[#00BAC8]/30 hover:text-[#04080E] text-[#00BAC8] font-bold text-[10px] rounded transition-all disabled:opacity-40"
                >
                  {simulating ? 'Simulating...' : 'Dispatch Inbound'}
                </button>
              </form>

              {simResult && (
                <div className="p-2 bg-[#080D15] border border-white/5 text-[9px] text-[#00E676] font-mono leading-normal rounded">
                  {simResult}
                </div>
              )}
            </div>
          </div>

          {/* User Credits / Rule Indicator */}
          <div className="space-y-2">
            <div className="p-3 bg-white/2 border border-white/5 rounded-xl text-[10px] text-gray-500 font-mono space-y-1">
              <div className="flex items-center justify-between">
                <span>Tenant:</span>
                <strong className="text-[#00BAC8]">{userRole === 'admin' ? 'Operator Central (Multi)' : 'BlueLine Staffing'}</strong>
              </div>
              <div className="flex items-center justify-between">
                <span>Role:</span>
                <strong className="text-gray-300">{userRole === 'admin' ? 'Operator Admin' : 'Client Coordinator'}</strong>
              </div>
              <div className="flex items-center justify-between">
                <span>Operator:</span>
                <strong className="text-gray-300">{userRole === 'admin' ? 'Aditya Dhillon' : 'BlueLine Client'}</strong>
              </div>
            </div>

            <button
              onClick={() => {
                setMode('landing');
                setUserRole(null);
              }}
              className="w-full py-2 bg-red-500/10 hover:bg-red-500 text-red-400 hover:text-white border border-red-500/20 text-[11px] font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 font-mono cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" /> Sign Out
            </button>
          </div>
        </aside>

        {/* Content Workspace */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6">
          {tab === 'dashboard' && (
            <MasterDashboard 
              candidates={candidates}
              shifts={shifts}
              reviewItems={reviewQueue}
              isAdmin={userRole === 'admin'}
            />
          )}

          {tab === 'live' && (
            <LiveDashboard 
              candidates={candidates}
              shifts={shifts}
              reviewItems={reviewQueue}
              onApproveReview={handleApproveReview}
              isAdmin={userRole === 'admin'}
            />
          )}

          {tab === 'pipeline' && (
            <CandidatePipeline
              candidates={candidates}
              onSelectCandidate={(cand) => {
                setSelectedCandidate(cand);
                setTab('audit');
              }}
              onAddCandidate={handleAddCandidate}
            />
          )}

          {tab === 'audit' && (
            <div className="h-full">
              {selectedCandidate ? (
                <CredentialAudit
                  candidate={selectedCandidate}
                  onUpdateCandidate={handleUpdateCandidate}
                  onClose={() => setSelectedCandidate(null)}
                />
              ) : (
                <div className="bg-[#0B121C] border border-white/5 rounded-xl p-8 text-center space-y-4 max-w-lg mx-auto mt-12">
                  <ShieldCheck className="w-12 h-12 text-[#00BAC8] mx-auto shrink-0" />
                  <h3 className="text-sm font-bold text-white font-display">11-Point Document Audit Room</h3>
                  <p className="text-xs text-gray-400 leading-relaxed font-sans">
                    Select any nurse from the pipeline board to initiate their AI-Vision licensing and credential audit checklist. Here you can mock upload certificates and verify PPD status.
                  </p>
                  <button
                    onClick={() => setTab('pipeline')}
                    className="px-4 py-2 bg-[#00BAC8] text-[#04080E] font-bold text-xs rounded-lg hover:opacity-90 transition-all"
                  >
                    Open Pipeline Board
                  </button>
                </div>
              )}
            </div>
          )}

          {tab === 'shifts' && (
            <ShiftMatching
              shifts={shifts}
              candidates={candidates}
              onAddShift={handleAddShift}
              onMatchShift={handleMatchShift}
            />
          )}

          {tab === 'reviews' && (
            <ReviewQueue
              reviewItems={reviewQueue}
              onApprove={handleApproveReview}
              onReject={handleRejectReview}
            />
          )}

          {tab === 'console' && (
            <LiveConsole
              logs={logs}
              onTriggerDailyCron={handleTriggerDailyCron}
              onClearConsole={handleClearConsole}
            />
          )}

          {tab === 'settings' && settings && (
            <SettingsPanel
              settings={settings}
              blacklist={blacklist}
              onUpdateSettings={handleUpdateSettings}
              onAddBlacklist={handleAddBlacklist}
            />
          )}
        </main>
      </div>
    </div>
  );
}
