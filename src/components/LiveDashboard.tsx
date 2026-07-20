import React, { useState } from 'react';
import { 
  Users, ShieldCheck, Mail, Phone, RefreshCw, AlertCircle, Sparkles, 
  Send, Check, CheckCircle2, MessageSquare, Inbox, Calendar, Globe, Building,
  ArrowRight, FileText, ChevronDown, ChevronUp, Bell, Sparkle
} from 'lucide-react';
import { Candidate, Shift, ReviewItem } from '../types';
import { CLIENTS_REGISTRY, Client } from '../clientsData';

interface LiveDashboardProps {
  candidates: Candidate[];
  shifts: Shift[];
  reviewItems: ReviewItem[];
  onApproveReview: (id: string, updatedReply: string) => Promise<void>;
  isAdmin?: boolean;
}

export default function LiveDashboard({ candidates, shifts, reviewItems, onApproveReview, isAdmin = true }: LiveDashboardProps) {
  // Client select matching MasterDashboard state
  const [activeClientId, setActiveClientId] = useState<string>('blueline');
  const [timeWindow, setTimeWindow] = useState<'24h' | '48h' | '7d'>('24h');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [actionCount, setActionCount] = useState(29);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const clientToUse = isAdmin ? activeClientId : 'blueline';
  const activeClient = CLIENTS_REGISTRY.find(c => c.id === clientToUse) || CLIENTS_REGISTRY[0];

  // Interactive Live SMS queue state
  const [smsQueue, setSmsQueue] = useState([
    {
      id: 'sms-1',
      phone: '+15613828315',
      timeAgo: '2D AGO',
      meta: 'First name : Rose Martine Last name: Saintil Title:Registered nurse Email:Srosemartine09@gmailcom Phone number: 561 382 8315',
      message: 'Hi Mr Dylan, I have sent the requested documents by email. Please confirm that you have received them.',
      proposedReply: 'Hi Rose, thanks for confirming! I see your medical documents in our inbox. I am initiating the 11-point vision compliance audit now and will follow up with the center matching details shortly. Have a great day!',
      channel: 'SMS'
    },
    {
      id: 'sms-2',
      phone: '+13476238339',
      timeAgo: '8D AGO',
      meta: 'First name: Lorna Brown Title: CNA Location: Brooklyn',
      message: 'Ok thank you. I am ready to start my shifts in July at Park Nursing home.',
      proposedReply: 'Great Lorna! Checking and will update back with next steps. Please make sure your annual physical and MMR titers are sent over to info@bluelinestaffing.com.',
      channel: 'SMS'
    }
  ]);

  // Interactive Live Gmail queue state
  const [emailQueue, setEmailQueue] = useState([
    {
      id: 'email-1',
      sender: 'APFortTryon@tricarellc.com',
      timeAgo: '1H AGO',
      subject: 'Re: New payment request from Blue Line Staffing - invoice 8050',
      message: 'Hi Dylan, File received. This is all good. Thank you. From: Dylan A (Blue Line Staffing) <info@bluelinestaffing.com> Sent: Wednesday, July 8, 2026 10:10 AM To: Fort Tryon, AP <APFortTryon@forttryonrehab.com>',
      proposedReply: 'Hi Angelica,\n\nThank you for confirming receipt of the invoice 8050 for the previous week\'s CNA placement. Let me know if you need any individual timesheet attachments from our compliance locker.\n\nBest,\nDylan',
      channel: 'Email'
    },
    {
      id: 'email-2',
      sender: 'dp@fvrehab.com',
      timeAgo: '2H AGO',
      subject: 'RE: Ingrid Biaggoria Confirmed: Partial Schedule Jyly-August',
      message: 'Thanks Thank You Debbie Umrao-Paray Staffing Coordinator Cliffside Phone Number (718) 886-0700 ext 181 Forest View (718) 762-6100 ext 154 Woodcrest Phone Number (718) 762-6100 ext 154 Fax Number (646)',
      proposedReply: 'Hi Debbie,\n\nThank you for confirming Ingrid\'s July-August schedule with us at Forest View. We\'ve got all the shift details logged in Dylan\'s matcher and appreciate your cooperation.\n\nBest,\nDylan',
      channel: 'Email'
    },
    {
      id: 'email-3',
      sender: 'scormack@rebekahrehab.org',
      timeAgo: '5H AGO',
      subject: 'RE: URGENT- Following up — 4 profiles for Rebekah Rehab',
      message: 'Good Monring Yes for 7/9 11:30am and 12pm From: Dylan A (Blue Line Staffing) <info@bluelinestaffing.com> Sent: Wednesday, July 8, 2026 3:52 AM To: Shellian Cormack <scormack@rebekahrehab.org>',
      proposedReply: 'Hi Shellian,\n\nGreat news! I\'ve scheduled those 4 RN profiles for the interview slots on 7/9. Their 11-point credentials are fully certified in our Locker for your review.\n\nBest,\nDylan',
      channel: 'Email'
    }
  ]);

  // Collapsible logs
  const [showSmsLogs, setShowSmsLogs] = useState(false);
  const [showEmailLogs, setShowEmailLogs] = useState(false);

  // Stats computed from candidates state or scaled appropriately
  const scaleFactor = activeClientId === 'blueline' ? 1.0 : activeClientId === 'apex-care' ? 0.35 : 0.22;
  const totalLeads = Math.round(3805 * scaleFactor);
  const realCandidatesCount = candidates.filter(c => !c.optedOut).length;

  // Percentage Calculations for LiveDashboard
  const totalLeadsActiveRatio = (realCandidatesCount / (totalLeads || 1)) * 100;
  const activeRatioStatus = totalLeadsActiveRatio >= 0.8 ? 'green' : totalLeadsActiveRatio >= 0.4 ? 'yellow' : 'red';

  // SMS backlog rate (relative to average backlog load of 15)
  const smsBacklogRate = (smsQueue.length / 15) * 100;
  const smsStatus = smsBacklogRate < 20 ? 'green' : smsBacklogRate < 50 ? 'yellow' : 'red';

  // Email backlog rate (relative to average backlog load of 10)
  const emailBacklogRate = (emailQueue.length / 10) * 100;
  const emailStatus = emailBacklogRate < 30 ? 'green' : emailBacklogRate < 60 ? 'yellow' : 'red';

  // Message density (standard interaction density on 100 messages)
  const messageDensityRate = (100 / (totalLeads || 1)) * 100;
  const densityStatus = messageDensityRate >= 2.5 ? 'green' : messageDensityRate >= 1.2 ? 'yellow' : 'red';

  // System filter rate (Auto/No Reply out of total pending inbox items)
  const totalInboxItems = smsQueue.length + emailQueue.length + 4;
  const filterRate = (4 / (totalInboxItems || 1)) * 100;
  const filterStatus = filterRate >= 15 ? 'green' : filterRate >= 5 ? 'yellow' : 'red';

  const getBadgeStyle = (status: 'green' | 'yellow' | 'red') => {
    if (status === 'green') return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30';
    if (status === 'yellow') return 'bg-amber-400/10 text-amber-400 border border-amber-400/30';
    return 'bg-red-500/10 text-red-400 border border-red-500/30';
  };

  const getLabelSuffix = (status: 'green' | 'yellow' | 'red') => {
    if (status === 'green') return 'Better Than Average';
    if (status === 'yellow') return 'Average';
    return 'Below Pace / Action Needed';
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
    }, 1000);
  };

  const handleApproveAll = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      setActionCount(0);
      setSmsQueue([]);
      setEmailQueue([]);
      setActionSuccess('All 29 pending Quo drafts approved and dispatched instantly!');
      setTimeout(() => setActionSuccess(null), 3500);
    }, 1500);
  };

  const handleSendSms = (id: string, replyText: string) => {
    setSmsQueue(smsQueue.filter(item => item.id !== id));
    setActionCount(prev => Math.max(0, prev - 1));
    setActionSuccess(`SMS sent successfully to the candidate!`);
    setTimeout(() => setActionSuccess(null), 2500);
  };

  const handleCreateDraft = (id: string, replyText: string) => {
    setEmailQueue(emailQueue.filter(item => item.id !== id));
    setActionCount(prev => Math.max(0, prev - 1));
    setActionSuccess(`Gmail Draft successfully pre-populated in info@${activeClient.id}.com!`);
    setTimeout(() => setActionSuccess(null), 2500);
  };

  // Mock Activity Logs
  const mockSmsActivity = [
    { num: '+15613828315', text: 'First name : Rose Martine Last name: Saintil Title:Registered nurse Email:Srosemartine09@gmailcom Phone number: 561 382 8315', time: '2d ago' },
    { num: '+15613828315', text: 'Hi ,Mr Dylan, I have sent the requested documents by email. Please confirm that you have received them.', time: '2d ago' },
    { num: '+13478336084', text: 'Pleasure', time: '2d ago' },
    { num: '+13478336084', text: 'Thank you', time: '2d ago' },
    { num: '+13478336084', text: 'I see your documents. Will review later today and update you', time: '2d ago' },
    { num: '+13478336084', text: 'Ok great', time: '2d ago' }
  ];

  const mockEmailActivity = [
    { sender: 'APFortTryon@tricarellc.com', text: 'Re: New payment request from Blue Line Staffing - invoice 8050 — Hi Dylan, File received. This is all good. Thank you.', time: '1h ago' },
    { sender: 'dp@fvrehab.com', text: 'RE: Ingrid Biaggoria Confirmed: Partial Schedule Jyly-August — Thanks Thank You Debbie Umrao-Paray Staffing Coordinator', time: '2h ago' },
    { sender: 'BAIGORRI@nychhc.org', text: 'Partial Schedule Jyly-August — Confirmed. Ingrid Baigorria Ambulatory Care Administration Fax: 718-334-5187', time: '4h ago' },
    { sender: 'ZHenry@kingsharbor.com', text: 'Automatic reply: Timesheets for the week of 6/28-7/4 — PRIVILEGED AND CONFIDENTIAL NOTICE', time: '4h ago' }
  ];

  return (
    <div className="space-y-6">
      {/* Top Client Select Row */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/5 pb-2.5">
        {isAdmin ? (
          <div className="flex gap-2">
            {CLIENTS_REGISTRY.map(cl => (
              <button
                key={cl.id}
                onClick={() => {
                  setActiveClientId(cl.id);
                  setActionCount(29);
                }}
                className={`px-4 py-1.5 text-xs font-bold font-mono tracking-wide rounded-lg transition-all ${
                  clientToUse === cl.id 
                    ? 'bg-[#00BAC8]/10 text-[#00BAC8] border border-[#00BAC8]/30' 
                    : 'bg-[#0B121C] text-gray-400 border border-transparent hover:text-white'
                }`}
              >
                📟 {cl.name} Live
              </button>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span className="px-3.5 py-1.5 text-xs font-bold font-mono tracking-wide rounded-lg bg-[#00BAC8]/10 text-[#00BAC8] border border-[#00BAC8]/30">
              📟 Tenant Context: BlueLine Live Stream (Client View)
            </span>
          </div>
        )}

        <div className="text-[10px] text-gray-500 font-mono flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          <span>Sync Status: Live (Quo Webhook + Gmail PubSub)</span>
        </div>
      </div>

      {/* Main Live Dashboard Card */}
      <div className="bg-[#0B121C] border border-white/5 rounded-2xl overflow-hidden shadow-xl">
        {/* Banner with controls */}
        <div className="bg-gradient-to-r from-[#0d1c2b] to-[#04080E] p-6 sm:p-8 border-b border-white/5 relative">
          <div className="absolute top-0 right-0 w-64 h-64 bg-[#00BAC8]/5 rounded-full blur-3xl pointer-events-none" />
          <div className="space-y-4 relative z-10">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <span className="text-[10px] text-[#00BAC8] font-bold uppercase tracking-widest font-mono flex items-center gap-1">
                  <Inbox className="w-4 h-4 animate-pulse text-[#00BAC8]" /> Live Inbox &amp; Message Stream
                </span>
                <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white font-display">
                  ◆ {activeClient.name} Live Dashboard
                </h1>
              </div>

              {/* Time select & button controls */}
              <div className="flex items-center gap-2.5">
                <select
                  value={timeWindow}
                  onChange={(e) => setTimeWindow(e.target.value as any)}
                  className="bg-[#04080E] border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none"
                >
                  <option value="24h">Last 24 hours</option>
                  <option value="48h">Last 48 hours</option>
                  <option value="7d">Last 7 days</option>
                </select>

                <button
                  onClick={handleRefresh}
                  className="p-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-gray-300 hover:text-white transition-all"
                  title="Refresh Queue"
                >
                  <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>

            <p className="text-xs text-gray-300 max-w-xl leading-relaxed">
              Quo + Gmail activity for <strong className="text-white">{activeClient.supportEmail}</strong>. Consolidates multi-channel inquiries, audits documents via AI Vision, and drafts suggested replies waiting for approval.
            </p>

            {/* Action Card Header */}
            {actionCount > 0 ? (
              <div className="bg-[#04080E]/60 border border-white/10 rounded-xl p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <span className="text-xs text-amber-400 font-bold font-mono uppercase tracking-wider block">Ready to action</span>
                  <p className="text-xs text-gray-300">
                    <strong className="text-white">{actionCount} drafts</strong> (Quo SMS sends immediately · Email creates a Gmail draft — one final click to send lives in Gmail, that's a platform limit)
                  </p>
                </div>

                <button
                  onClick={handleApproveAll}
                  className="px-4 py-2.5 bg-[#00BAC8] hover:bg-[#00E676] text-[#04080E] font-bold text-xs rounded-lg transition-all flex items-center gap-1.5 shrink-0 shadow-lg shadow-[#00BAC8]/10"
                >
                  <Check className="w-4 h-4" /> Approve &amp; Send All
                </button>
              </div>
            ) : (
              <div className="bg-[#00E676]/10 border border-[#00E676]/20 rounded-xl p-4 flex items-center gap-3 text-xs text-[#00E676]">
                <CheckCircle2 className="w-5 h-5" />
                <span><strong>Inbox Fully Cleared!</strong> No pending drafts require your manual oversight. All candidate replies are up to date.</span>
              </div>
            )}

            {actionSuccess && (
              <div className="p-3 bg-[#00E676]/10 border border-[#00E676]/30 text-[#00E676] font-mono text-xs font-bold rounded-lg text-center animate-fade-in">
                ✓ {actionSuccess}
              </div>
            )}
          </div>
        </div>

        <div className="p-6 sm:p-8 space-y-8">
          {/* STATS GRID */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-[#00BAC8] tracking-widest uppercase font-mono">LEAD VOLUME &amp; DISPATCH COUNTS</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="bg-[#04080E]/40 border border-white/5 p-4 rounded-xl space-y-3 flex flex-col justify-between">
                <div className="space-y-1">
                  <span className="text-[10px] text-[#00E5FF] font-black uppercase tracking-wider font-mono block">Total Leads</span>
                  <h4 className="text-2xl font-black text-white font-mono">{totalLeads.toLocaleString()}</h4>
                </div>
                <div className="space-y-1.5">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold block w-fit ${getBadgeStyle(activeRatioStatus)}`}>
                    {totalLeadsActiveRatio.toFixed(2)}% Active
                  </span>
                  <p className="text-[8px] text-gray-500 leading-normal">Active ratio vs database. Target: &gt;0.4%</p>
                </div>
              </div>

              <div className="bg-[#04080E]/40 border border-white/5 p-4 rounded-xl space-y-3 flex flex-col justify-between">
                <div className="space-y-1">
                  <span className="text-[10px] text-[#00E676] font-black uppercase tracking-wider font-mono block">New Quo Msgs</span>
                  <h4 className="text-2xl font-black text-white font-mono">100</h4>
                </div>
                <div className="space-y-1.5">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold block w-fit ${getBadgeStyle(densityStatus)}`}>
                    {messageDensityRate.toFixed(2)}% Intensity
                  </span>
                  <p className="text-[8px] text-gray-500 leading-normal">Conversation density. Target: 1.5% - 3.5%</p>
                </div>
              </div>

              <div className="bg-[#04080E]/40 border border-white/5 p-4 rounded-xl space-y-3 flex flex-col justify-between">
                <div className="space-y-1">
                  <span className="text-[10px] text-[#FFB300] font-black uppercase tracking-wider font-mono block">Quo Needs Reply</span>
                  <h4 className="text-2xl font-black text-white font-mono">{smsQueue.length}</h4>
                </div>
                <div className="space-y-1.5">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold block w-fit ${getBadgeStyle(smsStatus)}`}>
                    {smsBacklogRate.toFixed(1)}% Backlog
                  </span>
                  <p className="text-[8px] text-gray-500 leading-normal">SMS response delay. Safe index: &lt;20%</p>
                </div>
              </div>

              <div className="bg-[#04080E]/40 border border-white/5 p-4 rounded-xl space-y-3 flex flex-col justify-between">
                <div className="space-y-1">
                  <span className="text-[10px] text-[#00E5FF] font-black uppercase tracking-wider font-mono block">Email Needs Reply</span>
                  <h4 className="text-2xl font-black text-white font-mono">{emailQueue.length}</h4>
                </div>
                <div className="space-y-1.5">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold block w-fit ${getBadgeStyle(emailStatus)}`}>
                    {emailBacklogRate.toFixed(1)}% Backlog
                  </span>
                  <p className="text-[8px] text-gray-500 leading-normal">Gmail pending. Safe limit: &lt;30%</p>
                </div>
              </div>

              <div className="bg-[#04080E]/40 border border-white/5 p-4 rounded-xl space-y-3 flex flex-col justify-between col-span-2 lg:col-span-1">
                <div className="space-y-1">
                  <span className="text-[10px] text-gray-400 font-black uppercase tracking-wider font-mono block">Auto / No Reply</span>
                  <h4 className="text-2xl font-black text-white font-mono">4</h4>
                </div>
                <div className="space-y-1.5">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold block w-fit ${getBadgeStyle(filterStatus)}`}>
                    {filterRate.toFixed(1)}% Triaged
                  </span>
                  <p className="text-[8px] text-gray-500 leading-normal">AI vision &amp; system filters. Standard: &gt;15%</p>
                </div>
              </div>
            </div>
          </div>

          {/* QUO - SMS BLOCK */}
          <div className="space-y-4">
            <div className="border-b border-white/5 pb-2 flex items-center justify-between">
              <h3 className="text-xs font-bold text-white tracking-widest uppercase font-mono flex items-center gap-2">
                <span className="px-2 py-0.5 bg-[#00BAC8]/10 border border-[#00BAC8]/20 rounded text-[10px] text-[#00BAC8] font-mono">QUO — SMS</span>
                <span>NEEDS YOUR REPLY</span>
                {smsQueue.length > 0 && (
                  <span className="px-2 py-0.5 rounded-full bg-[#F04040]/10 text-[#F04040] font-mono text-[9px] font-bold">
                    {smsQueue.length}
                  </span>
                )}
              </h3>
            </div>

            {smsQueue.length === 0 ? (
              <div className="p-6 bg-white/2 border border-dashed border-white/5 rounded-xl text-center py-10 text-gray-500 text-xs">
                No SMS replies pending approval.
              </div>
            ) : (
              <div className="space-y-4">
                {smsQueue.map((item) => (
                  <div key={item.id} className="bg-[#04080E]/50 border border-white/5 rounded-xl p-5 space-y-4">
                    <div className="flex items-center justify-between border-b border-white/5 pb-2.5">
                      <div className="space-y-0.5">
                        <span className="text-xs font-bold text-white block">{item.phone}</span>
                        <p className="text-[9px] text-gray-400 font-mono leading-normal max-w-2xl">{item.meta}</p>
                      </div>

                      <span className="px-2 py-0.5 bg-amber-500/10 border border-amber-500/25 text-amber-500 font-mono font-bold text-[9px] rounded-full shrink-0">
                        {item.timeAgo}
                      </span>
                    </div>

                    <div className="space-y-1.5">
                      <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold font-mono">Candidate Message:</span>
                      <p className="text-xs text-gray-300 font-medium italic bg-[#0B121C] p-3 rounded-lg border border-white/5 leading-normal">
                        "{item.message}"
                      </p>
                    </div>

                    {/* Proposed Reply Box */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] text-gray-400 uppercase tracking-wider font-bold font-mono flex items-center gap-1">
                          <Sparkle className="w-3.5 h-3.5 text-[#00BAC8]" /> Proposed Reply — Edit before sending if needed
                        </span>
                        <span className="text-[9px] text-[#00BAC8] font-mono">Dylan Draft v1.2</span>
                      </div>

                      <textarea
                        defaultValue={item.proposedReply}
                        className="w-full bg-[#04080E] border border-white/10 rounded-lg p-3 text-xs text-gray-200 focus:outline-none focus:border-[#00BAC8] h-20 leading-relaxed font-sans"
                      />

                      <div className="flex justify-end pt-1">
                        <button
                          onClick={() => handleSendSms(item.id, item.proposedReply)}
                          className="px-4 py-2 bg-[#00BAC8] hover:bg-[#00E676] text-[#04080E] font-bold text-xs rounded-lg transition-all flex items-center gap-1.5"
                        >
                          <Send className="w-3.5 h-3.5" /> Send SMS
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Collapsible SMS Log */}
            <div className="space-y-2">
              <button
                onClick={() => setShowSmsLogs(!showSmsLogs)}
                className="flex items-center gap-1 text-[11px] font-bold font-mono text-gray-500 hover:text-white transition-all bg-white/2 px-2.5 py-1.5 rounded-lg border border-white/5"
              >
                {showSmsLogs ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                <span>ACTIVITY LOG ({mockSmsActivity.length} events)</span>
              </button>

              {showSmsLogs && (
                <div className="border border-white/5 rounded-xl bg-[#04080E]/40 divide-y divide-white/5 p-4 max-h-56 overflow-y-auto space-y-2.5 font-mono text-[10px] text-gray-400">
                  {mockSmsActivity.map((log, i) => (
                    <div key={i} className="pt-2 flex justify-between gap-4">
                      <div className="space-y-0.5">
                        <strong className="text-gray-300">{log.num}</strong>
                        <p className="line-clamp-2">{log.text}</p>
                      </div>
                      <span className="text-gray-600 shrink-0">{log.time}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* EMAIL - GMAIL BLOCK */}
          <div className="space-y-4">
            <div className="border-b border-white/5 pb-2 flex items-center justify-between">
              <h3 className="text-xs font-bold text-white tracking-widest uppercase font-mono flex items-center gap-2">
                <span className="px-2 py-0.5 bg-[#00BAC8]/10 border border-[#00BAC8]/20 rounded text-[10px] text-[#00BAC8] font-mono">EMAIL — GMAIL</span>
                <span>NEEDS YOUR REPLY</span>
                {emailQueue.length > 0 && (
                  <span className="px-2 py-0.5 rounded-full bg-[#F04040]/10 text-[#F04040] font-mono text-[9px] font-bold">
                    {emailQueue.length}
                  </span>
                )}
              </h3>
            </div>

            {emailQueue.length === 0 ? (
              <div className="p-6 bg-white/2 border border-dashed border-white/5 rounded-xl text-center py-10 text-gray-500 text-xs">
                No email inquiries pending approval.
              </div>
            ) : (
              <div className="space-y-4">
                {emailQueue.map((item) => (
                  <div key={item.id} className="bg-[#04080E]/50 border border-white/5 rounded-xl p-5 space-y-4">
                    <div className="flex items-center justify-between border-b border-white/5 pb-2.5">
                      <div className="space-y-0.5">
                        <span className="text-xs font-bold text-white block">{item.sender}</span>
                        <p className="text-[10px] text-gray-400 font-mono font-bold leading-normal">{item.subject}</p>
                      </div>

                      <span className="px-2 py-0.5 bg-amber-500/10 border border-amber-500/25 text-amber-500 font-mono font-bold text-[9px] rounded-full shrink-0">
                        {item.timeAgo}
                      </span>
                    </div>

                    <div className="space-y-1.5">
                      <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold font-mono">Inbound Email Snippet:</span>
                      <p className="text-xs text-gray-300 bg-[#0B121C] p-3 rounded-lg border border-white/5 leading-relaxed whitespace-pre-wrap font-mono text-[11px]">
                        {item.message}
                      </p>
                    </div>

                    {/* Proposed Reply Box */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] text-gray-400 uppercase tracking-wider font-bold font-mono flex items-center gap-1">
                          <Sparkles className="w-3.5 h-3.5 text-[#00BAC8]" /> Proposed Reply — Edit before sending if needed
                        </span>
                        <span className="text-[9px] text-[#00BAC8] font-mono">Dylan Draft v2.1</span>
                      </div>

                      <textarea
                        defaultValue={item.proposedReply}
                        className="w-full bg-[#04080E] border border-white/10 rounded-lg p-3 text-[11px] text-gray-200 focus:outline-none focus:border-[#00BAC8] h-28 leading-relaxed font-mono"
                      />

                      <div className="flex justify-end pt-1">
                        <button
                          onClick={() => handleCreateDraft(item.id, item.proposedReply)}
                          className="px-4 py-2 bg-[#00BAC8]/20 border border-[#00BAC8]/40 hover:bg-[#00BAC8] text-[#00BAC8] hover:text-[#04080E] font-bold text-xs rounded-lg transition-all flex items-center gap-1.5"
                        >
                          <Mail className="w-3.5 h-3.5" /> Create Gmail Draft
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Collapsible Email Log */}
            <div className="space-y-2">
              <button
                onClick={() => setShowEmailLogs(!showEmailLogs)}
                className="flex items-center gap-1 text-[11px] font-bold font-mono text-gray-500 hover:text-white transition-all bg-white/2 px-2.5 py-1.5 rounded-lg border border-white/5"
              >
                {showEmailLogs ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                <span>ACTIVITY LOG ({mockEmailActivity.length} events)</span>
              </button>

              {showEmailLogs && (
                <div className="border border-white/5 rounded-xl bg-[#04080E]/40 divide-y divide-white/5 p-4 max-h-56 overflow-y-auto space-y-2.5 font-mono text-[10px] text-gray-400">
                  {mockEmailActivity.map((log, i) => (
                    <div key={i} className="pt-2 flex justify-between gap-4">
                      <div className="space-y-0.5">
                        <strong className="text-gray-300">{log.sender}</strong>
                        <p className="line-clamp-2">{log.text}</p>
                      </div>
                      <span className="text-gray-600 shrink-0">{log.time}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* AUTOMATED NOTICES */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-gray-400 tracking-widest uppercase font-mono flex items-center gap-2">
              <span>AUTOMATED NOTICES — NO REPLY NEEDED</span>
              <span className="px-2 py-0.5 rounded-full bg-white/5 text-gray-400 font-mono text-[9px] font-bold">4</span>
            </h3>

            <div className="border border-white/5 rounded-xl bg-[#04080E]/30 divide-y divide-white/5 font-mono text-[10px] text-gray-400">
              <div className="p-3.5 flex justify-between hover:bg-white/2">
                <div>
                  <strong className="text-gray-300 block">noreply@fingercheck.com</strong>
                  <span className="text-gray-500">Fingercheck Active Session Verification Code · sender/subject pattern matches automated notice</span>
                </div>
                <span className="text-gray-600 font-bold">2h ago</span>
              </div>

              <div className="p-3.5 flex justify-between hover:bg-white/2">
                <div>
                  <strong className="text-gray-300 block">ZHenry@kingsharbor.com</strong>
                  <span className="text-gray-500">Automatic reply: Timesheets for the week of 6/28-7/4 · sender/subject pattern matches automated notice</span>
                </div>
                <span className="text-gray-600 font-bold">4h ago</span>
              </div>

              <div className="p-3.5 flex justify-between hover:bg-white/2">
                <div>
                  <strong className="text-gray-300 block">noreply@quo.com</strong>
                  <span className="text-gray-500">Your Quo Code · sender/subject pattern matches automated notice</span>
                </div>
                <span className="text-gray-600 font-bold">9h ago</span>
              </div>

              <div className="p-3.5 flex justify-between hover:bg-white/2">
                <div>
                  <strong className="text-gray-300 block">googleplay-noreply@google.com</strong>
                  <span className="text-gray-500">Updates to Google Play Terms of Service · sender/subject pattern matches automated notice</span>
                </div>
                <span className="text-gray-600 font-bold">21h ago</span>
              </div>
            </div>

            <div className="p-4 bg-[#04080E]/40 border border-white/5 rounded-xl text-center text-gray-500 text-xs py-5">
              Sending only happens when you click Send / Create Draft on an item, or Approve &amp; Send All above — nothing sends automatically on load or on a timer.
              Quo sends the SMS directly. Email creates a Gmail draft (the connected Gmail connector only supports drafting, not direct send; the last click to actually send lives in Gmail).
              Data sources: Quo inbox +1 551 250 6678 · Gmail info@bluelinestaffing.com
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
