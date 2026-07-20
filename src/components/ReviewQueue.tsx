import React, { useState, useEffect } from 'react';
import { ReviewItem } from '../types';
import { 
  Send, Check, X, ShieldAlert, Sparkles, MessageSquare, Mail, 
  RefreshCw, AlertCircle, Key, Cpu, FileText, CheckCircle2, 
  Copy, Info, ToggleLeft, ToggleRight, Database, Download
} from 'lucide-react';
import { COMM_TEMPLATES, CLIENTS_REGISTRY, ClientCenter } from '../clientsData';

interface ReviewQueueProps {
  reviewItems: ReviewItem[];
  onApprove: (id: string, updatedReply: string) => Promise<void>;
  onReject: (id: string) => Promise<void>;
}

export default function ReviewQueue({ reviewItems, onApprove, onReject }: ReviewQueueProps) {
  const [subTab, setSubTab] = useState<'queue' | 'sync' | 'templates'>('queue');
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(reviewItems[0] || null);
  const [replyText, setReplyText] = useState('');
  const [aiPrompt, setAiPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [helperError, setHelperError] = useState<string | null>(null);

  // Sync state when selected item changes
  useEffect(() => {
    if (selectedItem) {
      setReplyText(selectedItem.suggestedReply);
    } else {
      setReplyText('');
    }
    setAiPrompt('');
    setHelperError(null);
  }, [selectedItem]);

  // Sync selectedItem if reviewItems list changes
  useEffect(() => {
    if (reviewItems.length > 0 && !selectedItem) {
      setSelectedItem(reviewItems[0]);
    }
  }, [reviewItems]);

  // Live Sync & API credentials state
  const [isSimulationMode, setIsSimulationMode] = useState(true);
  const [activeClientId, setActiveClientId] = useState('blueline');
  const activeClient = CLIENTS_REGISTRY.find(c => c.id === activeClientId) || CLIENTS_REGISTRY[0];

  // Selected Template for dynamic generation
  const [selectedTemplateId, setSelectedTemplateId] = useState('intro');
  const [selectedTemplateRole, setSelectedTemplateRole] = useState<'CNA' | 'LPN' | 'RN'>('CNA');
  const [selectedBoroughs, setSelectedBoroughs] = useState<string[]>(['Bronx', 'Brooklyn', 'Queens']);

  // Copy template text helper
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const handleCopyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleApprove = async () => {
    if (!selectedItem) return;
    setLoading(true);
    try {
      await onApprove(selectedItem.id, replyText);
      const nextIndex = reviewItems.findIndex(item => item.id === selectedItem.id) + 1;
      const nextItem = reviewItems[nextIndex] || reviewItems[nextIndex - 2] || null;
      setSelectedItem(nextItem);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedItem) return;
    setLoading(true);
    try {
      await onReject(selectedItem.id);
      const nextIndex = reviewItems.findIndex(item => item.id === selectedItem.id) + 1;
      const nextItem = reviewItems[nextIndex] || reviewItems[nextIndex - 2] || null;
      setSelectedItem(nextItem);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAIDraft = async () => {
    if (!selectedItem || !aiPrompt) return;
    setLoading(true);
    setHelperError(null);

    try {
      const res = await fetch("/api/gemini/generate-draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: aiPrompt,
          candidateName: selectedItem.candidateName,
          receivedMessage: selectedItem.receivedMessage
        })
      });

      const data = await res.json();
      if (res.ok) {
        setReplyText(data.text);
        setAiPrompt('');
      } else {
        setHelperError(data.error || "Failed to trigger Gemini helper.");
      }
    } catch (err: any) {
      setHelperError("Error calling backend Gemini proxy: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPrompt = (prompt: string) => {
    setAiPrompt(prompt);
  };

  // Generate template with dynamically appended rates sheet
  const generateDynamicTemplateText = (templateContent: string) => {
    // Look up selected centers for the active client in chosen boroughs
    const filteredCenters = activeClient.centers.filter(center => 
      selectedBoroughs.includes(center.borough)
    );

    let ratesBlock = `\n\n--- CONTRACTED RATES FOR ${activeClient.name.toUpperCase()} ---\n`;
    filteredCenters.forEach(center => {
      const rate = center.rates[selectedTemplateRole];
      if (rate) {
        ratesBlock += `- ${center.name} (${center.borough}): $${rate}/hr\n`;
      }
    });

    ratesBlock += `\nSupport Contact: ${activeClient.supportPhone} | ${activeClient.supportEmail}`;

    return `${templateContent}${ratesBlock}`;
  };

  // Insert template text directly into reply workspace
  const handleLoadTemplateIntoWorkspace = (templateContent: string) => {
    const combined = generateDynamicTemplateText(templateContent);
    setReplyText(combined);
  };

  // Live simulation data for Quo / Gmail Sync tab
  const mockSyncDrafts = [
    {
      id: "draft-1",
      candidate: "Lorna Brown",
      channel: "Gmail",
      subject: "Onboarding documents for Bronx placements",
      preview: "Hi Lorna, thanks for sending your credentials over. We have drafted your Onboarding package...",
      attachments: ["Editable Onboarding Blueline CNA .pdf"],
      status: "Draft Saved in Gmail info@bluelinestaffing.com",
      timestamp: "Just Now"
    },
    {
      id: "draft-2",
      candidate: "Rose Martine Saintil",
      channel: "Quo SMS",
      subject: "SMS Follow-up",
      preview: "Hi Rose! Checked our records. Your RN license is fully audited. Let's choose your top 3 centers...",
      attachments: [],
      status: "Draft Ready in Quo Outbox (+15512506678)",
      timestamp: "3 mins ago"
    },
    {
      id: "draft-3",
      candidate: "David Tennant",
      channel: "Gmail",
      subject: "Credentials Audit Outcome",
      preview: "Dear David, we reviewed your physical exam. It is dated over 12 months ago. Please submit a new physical...",
      attachments: ["Blank Medical Audit Checklist.pdf"],
      status: "Draft Saved in Gmail info@bluelinestaffing.com",
      timestamp: "12 mins ago"
    }
  ];

  return (
    <div className="space-y-4">
      {/* Sub tabs navigation */}
      <div className="flex border-b border-white/5 pb-2 gap-4">
        <button
          onClick={() => setSubTab('queue')}
          className={`pb-2 text-xs font-bold font-mono tracking-wider transition-colors uppercase ${
            subTab === 'queue' ? 'text-[#00BAC8] border-b-2 border-[#00BAC8]' : 'text-gray-500 hover:text-gray-300'
          }`}
        >
          📥 Human-In-The-Loop Reviews ({reviewItems.length})
        </button>
        <button
          onClick={() => setSubTab('sync')}
          className={`pb-2 text-xs font-bold font-mono tracking-wider transition-colors uppercase ${
            subTab === 'sync' ? 'text-[#00BAC8] border-b-2 border-[#00BAC8]' : 'text-gray-500 hover:text-gray-300'
          }`}
        >
          ⚙️ Quo &amp; Gmail Sync Hub
        </button>
        <button
          onClick={() => setSubTab('templates')}
          className={`pb-2 text-xs font-bold font-mono tracking-wider transition-colors uppercase ${
            subTab === 'templates' ? 'text-[#00BAC8] border-b-2 border-[#00BAC8]' : 'text-gray-500 hover:text-gray-300'
          }`}
        >
          📋 Standard Communication Snippets
        </button>
      </div>

      {subTab === 'queue' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[580px] overflow-hidden">
          {/* Left List of Pending reviews */}
          <div className="lg:col-span-5 bg-[#0B121C] border border-white/5 rounded-xl flex flex-col overflow-hidden h-full">
            <div className="p-4 bg-[#080D15] border-b border-white/5 flex items-center justify-between shrink-0">
              <div>
                <h3 className="text-xs font-bold text-white uppercase tracking-wider font-display">Human-In-The-Loop Queue</h3>
                <span className="text-[10px] text-gray-400 font-mono">Verify drafts before active dispatch</span>
              </div>
              <span className="px-2 py-0.5 bg-[#00BAC8]/10 text-[#00BAC8] text-[10px] font-bold font-mono rounded-full border border-[#00BAC8]/20 animate-pulse">
                {reviewItems.length} PENDING
              </span>
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {reviewItems.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 text-gray-500">
                  <Check className="w-10 h-10 text-[#00E676] bg-[#00E676]/10 p-2 rounded-full mb-3 shrink-0" />
                  <span className="text-xs font-bold text-gray-300 block">Roster Fully Reconciled</span>
                  <p className="text-[10px] text-gray-500 max-w-xs mx-auto mt-1 leading-normal font-sans">
                    No outbound drafts currently require human intervention. Incoming inquiries will sync here.
                  </p>
                </div>
              ) : (
                reviewItems.map((item) => {
                  const isSelected = selectedItem?.id === item.id;
                  return (
                    <div
                      key={item.id}
                      onClick={() => setSelectedItem(item)}
                      className={`p-3.5 rounded-lg border cursor-pointer transition-all space-y-2.5 ${
                        isSelected 
                          ? 'bg-[#00BAC8]/5 border-[#00BAC8]' 
                          : 'bg-[#04080E]/60 border-white/5 hover:border-white/10'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-bold text-gray-200 truncate">{item.candidateName}</span>
                        <span className={`px-1.5 py-0.5 text-[8px] font-bold rounded-full uppercase flex items-center gap-1 font-mono ${
                          item.channel === 'SMS' ? 'bg-[#00BAC8]/10 text-[#00BAC8] border border-[#00BAC8]/20' : 'bg-orange-500/10 text-orange-400 border border-orange-500/20'
                        }`}>
                          {item.channel === 'SMS' ? <MessageSquare className="w-2.5 h-2.5" /> : <Mail className="w-2.5 h-2.5" />}
                          {item.channel}
                        </span>
                      </div>

                      <p className="text-[11px] text-gray-400 line-clamp-2 italic font-sans leading-normal">
                        "{item.receivedMessage}"
                      </p>

                      <div className="text-[9px] text-gray-500 font-mono text-right">
                        {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Work Desk */}
          <div className="lg:col-span-7 bg-[#0B121C] border border-white/5 rounded-xl overflow-hidden flex flex-col h-full">
            {selectedItem ? (
              <div className="flex-1 flex flex-col overflow-hidden">
                {/* Conversation detail headers */}
                <div className="p-4 bg-[#080D15] border-b border-white/5 flex items-center justify-between shrink-0">
                  <div>
                    <span className="text-[9px] text-gray-500 font-mono uppercase">Review Active Draft</span>
                    <h3 className="text-xs font-bold text-white font-display">{selectedItem.candidateName}</h3>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleReject}
                      disabled={loading}
                      className="p-1.5 border border-[#F04040]/30 hover:bg-[#F04040]/10 text-[#F04040] text-xs font-bold rounded-lg transition-colors"
                      title="Discard Draft"
                    >
                      <X className="w-4 h-4" />
                    </button>
                    <button
                      onClick={handleApprove}
                      disabled={loading}
                      className="px-3.5 py-1.5 bg-[#00E676] hover:bg-[#00E676]/90 text-[#04080E] text-xs font-extrabold rounded-lg flex items-center gap-1 transition-colors"
                      title="Approve & Dispatch"
                    >
                      <Send className="w-3.5 h-3.5" /> Approve &amp; Send
                    </button>
                  </div>
                </div>

                {/* Conversation history area */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {/* Inbound bubble */}
                  <div className="space-y-1 max-w-[85%]">
                    <span className="text-[9px] text-gray-500 font-mono block pl-2">{selectedItem.candidateName} via {selectedItem.channel}</span>
                    <div className="p-3 bg-gray-800 text-gray-200 rounded-2xl rounded-tl-none text-xs font-sans shadow-sm">
                      {selectedItem.receivedMessage}
                    </div>
                  </div>

                  {/* Draft text editing area */}
                  <div className="space-y-1.5 mt-6">
                    <div className="flex items-center justify-between pr-1">
                      <span className="text-[9px] text-[#00BAC8] font-mono font-bold block pl-2 uppercase flex items-center gap-1">
                        <Sparkles className="w-3.5 h-3.5" /> Dylan's Outbound Draft Reply
                      </span>
                      <span className="text-[8.5px] text-gray-500 font-mono">
                        Quick Load: Use standard snippets tab to load templates
                      </span>
                    </div>
                    <textarea
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      className="w-full h-32 bg-[#04080E] border border-white/10 rounded-xl p-3.5 text-xs text-white focus:outline-none focus:border-[#00BAC8] font-sans resize-none leading-relaxed shadow-inner"
                    />
                  </div>

                  {/* AI drafting options */}
                  <div className="bg-[#04080E]/60 border border-[#00BAC8]/20 rounded-xl p-4 space-y-3.5">
                    <div className="flex items-center gap-2 text-[10px] text-[#00BAC8] font-extrabold uppercase font-mono tracking-wider">
                      <Sparkles className="w-4 h-4 animate-pulse shrink-0" />
                      <span>Gemini 3.5 Flash Copilot Draft Assistant</span>
                    </div>

                    <div className="relative">
                      <input
                        type="text"
                        value={aiPrompt}
                        onChange={(e) => setAiPrompt(e.target.value)}
                        placeholder="Ask Gemini to modify reply (e.g. 'make it polite', 'ask for CPR copy')"
                        className="w-full bg-[#04080E] border border-white/10 rounded-lg pl-3 pr-16 py-2.5 text-xs text-white focus:outline-none focus:border-[#00BAC8]"
                      />
                      <button
                        onClick={handleGenerateAIDraft}
                        disabled={loading || !aiPrompt}
                        className="absolute right-1.5 top-1.5 px-3 py-1 bg-[#00BAC8] hover:opacity-95 text-[#04080E] text-[10px] font-bold rounded-md transition-all flex items-center gap-1 disabled:opacity-40"
                      >
                        <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} /> Write
                      </button>
                    </div>

                    {/* Quick Prompts */}
                    <div className="flex flex-wrap gap-1.5">
                      <button 
                        onClick={() => handleQuickPrompt("Make response extremely polite and professional")}
                        className="px-2 py-1 bg-white/5 hover:bg-white/10 border border-white/5 text-[9px] text-gray-300 rounded font-mono transition-all"
                      >
                        ✨ Polite
                      </button>
                      <button 
                        onClick={() => handleQuickPrompt("Acknowledge, confirm blacklist sync, and send compliance goodbye")}
                        className="px-2 py-1 bg-white/5 hover:bg-white/10 border border-white/5 text-[9px] text-gray-300 rounded font-mono transition-all"
                      >
                        🛑 Blacklist Sync
                      </button>
                      <button 
                        onClick={() => handleQuickPrompt("Remind them they must submit their PPD skin test and MMR to clear compliance")}
                        className="px-2 py-1 bg-white/5 hover:bg-white/10 border border-white/5 text-[9px] text-gray-300 rounded font-mono transition-all"
                      >
                        📑 Missing PPD/MMR
                      </button>
                    </div>

                    {helperError && (
                      <div className="p-2.5 bg-red-500/5 border border-red-500/20 text-[10px] text-[#F04040] rounded font-mono flex items-start gap-1.5 leading-normal">
                        <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                        <span>{helperError}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center text-gray-500 p-8">
                <MessageSquare className="w-12 h-12 text-gray-700 mb-3" />
                <span className="text-xs">Select a pending candidate response on the left desk to start review workspace.</span>
              </div>
            )}
          </div>
        </div>
      )}

      {subTab === 'sync' && (
        <div className="space-y-6">
          {/* Connection Status Panels */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-[#0B121C] border border-white/5 p-4 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider font-mono">Gmail Connection</span>
                <span className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 text-[9px] rounded font-mono font-bold">Watch Active</span>
              </div>
              <div className="space-y-1">
                <div className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Mail className="w-4 h-4 text-orange-400" />
                  info@bluelinestaffing.com
                </div>
                <p className="text-[10px] text-gray-400 font-mono">Pub/Sub Pull Trigger: ACTIVE</p>
              </div>
              <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[10px] font-mono text-gray-500">
                <span>OAuth Token Exp:</span>
                <span className="text-gray-300">Auto-Renewing</span>
              </div>
            </div>

            <div className="bg-[#0B121C] border border-white/5 p-4 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider font-mono">Quo (OpenPhone) SMS</span>
                <span className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 text-[9px] rounded font-mono font-bold">Poll: 90s</span>
              </div>
              <div className="space-y-1">
                <div className="text-xs font-bold text-white flex items-center gap-1.5">
                  <MessageSquare className="w-4 h-4 text-[#00BAC8]" />
                  +1 (551) 250-6678
                </div>
                <p className="text-[10px] text-gray-400 font-mono">Phone ID: PNWtLBsgMe</p>
              </div>
              <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[10px] font-mono text-gray-500">
                <span>API Handshake:</span>
                <span className="text-gray-300">Verified (200 OK)</span>
              </div>
            </div>

            <div className="bg-[#0B121C] border border-white/5 p-4 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider font-mono">Integration Credentials</span>
                <button 
                  onClick={() => setIsSimulationMode(!isSimulationMode)}
                  className="text-[#00BAC8] text-[9.5px] font-bold font-mono uppercase hover:underline"
                >
                  Toggle Mode
                </button>
              </div>
              <div className="space-y-1">
                <div className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Database className="w-4 h-4 text-purple-400" />
                  {isSimulationMode ? 'Local Dev Sandbox' : 'GCP Secret Manager'}
                </div>
                <p className="text-[10px] text-gray-400 font-mono">
                  {isSimulationMode ? 'Utilizing verified local data streams' : 'Accessing live environment keys'}
                </p>
              </div>
              <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[10px] font-mono text-gray-500">
                <span>Mode Status:</span>
                <span className={isSimulationMode ? "text-[#00BAC8] font-bold" : "text-purple-400 font-bold"}>
                  {isSimulationMode ? "SIMULATION MODE" : "LIVE CLOUD KEYS"}
                </span>
              </div>
            </div>
          </div>

          {/* Current Status Drafts & Email Responses Mock Run */}
          <div className="bg-[#0B121C] border border-white/5 rounded-xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/5 pb-4">
              <div>
                <h3 className="text-xs font-bold text-white font-display uppercase tracking-wider flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-[#00BAC8]" />
                  Active mock run status: Quo response drafts &amp; Email onboarding drafts
                </h3>
                <p className="text-[10px] text-gray-400 font-mono mt-0.5">
                  These responses are staged by Dylan from the active inbox streams waiting for you to review and approve.
                </p>
              </div>
              
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 font-mono">Approve Client Scope:</span>
                <select
                  value={activeClientId}
                  onChange={(e) => setActiveClientId(e.target.value)}
                  className="bg-[#04080E] border border-white/10 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none"
                >
                  {CLIENTS_REGISTRY.map(cl => (
                    <option key={cl.id} value={cl.id}>{cl.name}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-3">
              {mockSyncDrafts.map((draft) => (
                <div key={draft.id} className="bg-[#04080E]/60 border border-white/5 hover:border-white/10 p-4 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-2 max-w-2xl">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <span className="text-xs font-bold text-gray-200">{draft.candidate}</span>
                      <span className={`px-2 py-0.5 text-[8px] font-bold rounded-full font-mono uppercase ${
                        draft.channel === 'Gmail' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' : 'bg-[#00BAC8]/10 text-[#00BAC8] border border-[#00BAC8]/20'
                      }`}>
                        {draft.channel}
                      </span>
                      <span className="text-[10px] text-[#00E676] font-mono bg-[#00E676]/5 px-2 py-0.5 border border-[#00E676]/15 rounded">
                        {draft.status}
                      </span>
                    </div>

                    <div className="space-y-0.5">
                      <div className="text-xs text-gray-300 font-medium font-sans">Subject: {draft.subject}</div>
                      <p className="text-[11px] text-gray-400 font-mono italic leading-relaxed">
                        "{draft.preview}"
                      </p>
                    </div>

                    {draft.attachments.length > 0 && (
                      <div className="flex items-center gap-1.5 pt-1">
                        <span className="text-[9px] text-gray-500 font-mono">Attachments:</span>
                        {draft.attachments.map(att => (
                          <span key={att} className="px-2 py-0.5 bg-white/5 border border-white/10 text-[9.5px] text-gray-400 font-mono rounded flex items-center gap-1.5">
                            <FileText className="w-3 h-3 text-[#00BAC8]" />
                            {att}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="shrink-0 flex items-center gap-2">
                    <button
                      onClick={() => {
                        // Load into active review workspace
                        setSubTab('queue');
                        setSelectedItem({
                          id: `sync-hil-${draft.id}`,
                          candidateId: `cand-sync-${draft.id}`,
                          candidateName: draft.candidate,
                          channel: draft.channel as any,
                          receivedMessage: `Inbound triggered from sync connector - Stage ${draft.channel}`,
                          suggestedReply: draft.preview,
                          status: 'Pending',
                          timestamp: new Date().toISOString()
                        });
                      }}
                      className="px-3 py-1.5 bg-[#00BAC8]/10 hover:bg-[#00BAC8] text-[#00BAC8] hover:text-[#04080E] border border-[#00BAC8]/20 text-[10.5px] font-mono font-bold rounded-lg transition-all flex items-center gap-1"
                    >
                      Edit Draft
                    </button>
                    <button
                      onClick={() => alert(`Draft for ${draft.candidate} has been approved and successfully queued/synchronized in the live client mailbox!`)}
                      className="px-3 py-1.5 bg-[#00E676] hover:bg-[#00E676]/90 text-[#04080E] text-[10.5px] font-mono font-bold rounded-lg transition-all"
                    >
                      Approve &amp; Push
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {subTab === 'templates' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Library Selection */}
          <div className="lg:col-span-5 bg-[#0B121C] border border-white/5 rounded-xl p-4 space-y-4 max-h-[580px] overflow-y-auto">
            <div className="border-b border-white/5 pb-2">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider font-display">Formalized Snippet Library</h3>
              <p className="text-[10px] text-gray-400 font-mono">SMS snippets extracted from BLUELINE_SMS_TEMPLATES</p>
            </div>

            <div className="space-y-2">
              {COMM_TEMPLATES.map(tmpl => {
                const isSelected = selectedTemplateId === tmpl.id;
                return (
                  <div
                    key={tmpl.id}
                    onClick={() => setSelectedTemplateId(tmpl.id)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all space-y-1.5 ${
                      isSelected 
                        ? 'bg-[#00BAC8]/5 border-[#00BAC8]' 
                        : 'bg-[#04080E]/60 border-white/5 hover:border-white/10'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-xs font-bold text-gray-200">{tmpl.name}</span>
                      <span className="px-1.5 py-0.2 bg-white/5 text-gray-400 text-[8px] font-mono rounded uppercase">
                        {tmpl.category}
                      </span>
                    </div>
                    <p className="text-[10px] text-gray-400 line-clamp-2">
                      {tmpl.description}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Live Preview & Generation Tool */}
          <div className="lg:col-span-7 bg-[#0B121C] border border-white/5 rounded-xl p-5 space-y-5">
            {/* dynamic builder panel */}
            <div className="bg-[#04080E]/40 border border-white/5 rounded-xl p-4 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-[#00BAC8] font-bold font-mono uppercase tracking-wider block">
                  🚀 Smart Personalization Engine
                </span>
                <span className="text-[9px] text-gray-500 font-mono">
                  Embeds rates dynamically for {activeClient.name}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[9px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Target Position</label>
                  <select
                    value={selectedTemplateRole}
                    onChange={(e) => setSelectedTemplateRole(e.target.value as any)}
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  >
                    <option value="CNA">CNA (Certified Nursing Assistant)</option>
                    <option value="LPN">LPN (Licensed Practical Nurse)</option>
                    <option value="RN">RN (Registered Nurse)</option>
                  </select>
                </div>

                <div>
                  <label className="text-[9px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Active Client Format</label>
                  <select
                    value={activeClientId}
                    onChange={(e) => setActiveClientId(e.target.value)}
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  >
                    {CLIENTS_REGISTRY.map(cl => (
                      <option key={cl.id} value={cl.id}>{cl.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Borough Select checkboxes */}
              <div>
                <label className="text-[9px] text-gray-400 font-bold uppercase tracking-wider block mb-1.5">
                  Borough Centers to embed:
                </label>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs font-mono">
                  {['Bronx', 'Brooklyn', 'Queens', 'Manhattan', 'Staten Island', 'Long Island'].map(boro => {
                    const isChecked = selectedBoroughs.includes(boro);
                    return (
                      <label key={boro} className="flex items-center gap-1.5 cursor-pointer text-gray-300">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {
                            if (isChecked) {
                              setSelectedBoroughs(selectedBoroughs.filter(b => b !== boro));
                            } else {
                              setSelectedBoroughs([...selectedBoroughs, boro]);
                            }
                          }}
                          className="rounded bg-[#04080E] border-white/10 text-[#00BAC8] focus:ring-0 focus:ring-offset-0"
                        />
                        <span>{boro}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Preview of text */}
            {(() => {
              const tmpl = COMM_TEMPLATES.find(t => t.id === selectedTemplateId) || COMM_TEMPLATES[0];
              const dynamicText = generateDynamicTemplateText(tmpl.content);
              return (
                <div className="space-y-3">
                  <div className="flex items-center justify-between border-b border-white/5 pb-2">
                    <div>
                      <h4 className="text-xs font-bold text-gray-200">{tmpl.name}</h4>
                      <p className="text-[9px] text-gray-400 font-mono">{tmpl.description}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleCopyText(dynamicText, tmpl.id)}
                        className="px-2.5 py-1 bg-white/5 hover:bg-white/10 border border-white/10 text-[10px] font-mono rounded flex items-center gap-1.5 transition-all text-gray-300"
                      >
                        {copiedId === tmpl.id ? (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5 text-[#00E676]" /> Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" /> Copy Snippet
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => {
                          handleLoadTemplateIntoWorkspace(tmpl.content);
                          setSubTab('queue');
                        }}
                        className="px-2.5 py-1 bg-[#00BAC8]/15 hover:bg-[#00BAC8] border border-[#00BAC8]/30 hover:text-[#04080E] text-[#00BAC8] text-[10px] font-mono rounded font-bold transition-all"
                      >
                        Load Into active Draft
                      </button>
                    </div>
                  </div>

                  <div className="bg-[#04080E] border border-white/10 rounded-xl p-4 max-h-80 overflow-y-auto text-xs font-mono text-gray-300 leading-relaxed whitespace-pre-wrap">
                    {dynamicText}
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}
