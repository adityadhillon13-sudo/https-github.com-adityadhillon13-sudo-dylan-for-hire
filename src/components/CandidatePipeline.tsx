import React, { useState } from 'react';
import { Candidate, CandidateRole } from '../types';
import { Search, Plus, Filter, User, Phone, Mail, MapPin, Tag, CheckCircle2, ShieldAlert } from 'lucide-react';

interface CandidatePipelineProps {
  candidates: Candidate[];
  onSelectCandidate: (candidate: Candidate) => void;
  onAddCandidate: (candidateData: {
    name: string;
    phone: string;
    email: string;
    role: CandidateRole;
    borough: Candidate['borough'];
  }) => Promise<void>;
}

const STAGES: Candidate['status'][] = ['Intake', 'Captured', 'Audited', 'Shift Matched', 'Placed'];

const ROLE_COLORS: Record<CandidateRole, string> = {
  CNA: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  LPN: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  RN: 'bg-[#00BAC8]/10 text-[#00BAC8] border-[#00BAC8]/30',
};

const STAGE_LABELS: Record<Candidate['status'], string> = {
  Intake: '📥 Inbound / Intake',
  Captured: '👤 Profile Captured',
  Audited: '📑 Documents Audited',
  'Shift Matched': '📅 Shift Matched',
  Placed: '✅ Placed / Working',
};

export default function CandidatePipeline({ candidates, onSelectCandidate, onAddCandidate }: CandidatePipelineProps) {
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    role: 'CNA' as CandidateRole,
    borough: 'Brooklyn' as Candidate['borough']
  });

  const [loading, setLoading] = useState(false);

  // Stats
  const cnaCount = candidates.filter(c => c.role === 'CNA' && !c.optedOut).length;
  const lpnCount = candidates.filter(c => c.role === 'LPN' && !c.optedOut).length;
  const rnCount = candidates.filter(c => c.role === 'RN' && !c.optedOut).length;

  const filteredCandidates = candidates.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase()) || 
                          c.phone.includes(search) || 
                          c.email.toLowerCase().includes(search.toLowerCase());
    const matchesRole = roleFilter === 'ALL' || c.role === roleFilter;
    return matchesSearch && matchesRole && !c.optedOut;
  });

  const getCandidatesInStage = (stage: Candidate['status']) => {
    return filteredCandidates.filter(c => c.status === stage);
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.phone || !formData.email) return;
    
    setLoading(true);
    try {
      await onAddCandidate(formData);
      setShowAddModal(false);
      setFormData({
        name: '',
        phone: '',
        email: '',
        role: 'CNA',
        borough: 'Brooklyn'
      });
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search & Filters */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B121C] border border-white/5 p-4 rounded-xl">
        <div className="flex items-center gap-3 shrink-0">
          <div className="px-3 py-1 bg-[#00BAC8]/10 text-[#00BAC8] text-xs font-semibold rounded border border-[#00BAC8]/20 font-mono">
            {candidates.filter(c => !c.optedOut).length} ACTIVE NURSES
          </div>
          <div className="text-xs text-gray-400 font-mono hidden sm:block">
            {cnaCount} CNA · {lpnCount} LPN · {rnCount} RN
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-500" />
            <input 
              type="text" 
              placeholder="Search by name, phone, email..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#04080E] border border-white/10 rounded-lg pl-9 pr-4 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
            />
          </div>

          <div className="flex items-center gap-1 bg-[#04080E] border border-white/10 rounded-lg p-0.5">
            {['ALL', 'CNA', 'LPN', 'RN'].map((role) => (
              <button
                key={role}
                onClick={() => setRoleFilter(role)}
                className={`px-3 py-1.5 text-[10px] font-bold rounded-md uppercase transition-all ${
                  roleFilter === role 
                    ? 'bg-[#00BAC8] text-[#04080E]' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {role}
              </button>
            ))}
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="px-3 py-2 bg-[#00BAC8] hover:opacity-90 text-[#04080E] font-bold text-xs rounded-lg flex items-center gap-1.5 shrink-0 transition-all ml-auto md:ml-0"
          >
            <Plus className="w-4 h-4" /> Add Candidate
          </button>
        </div>
      </div>

      {/* Kanban Pipeline Board */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 overflow-x-auto pb-4">
        {STAGES.map((stage) => {
          const stageCandidates = getCandidatesInStage(stage);
          return (
            <div key={stage} className="flex flex-col min-w-[220px] bg-[#0B121C] border border-white/5 rounded-xl h-[560px] overflow-hidden">
              {/* Header */}
              <div className="p-3 bg-[#080D15] border-b border-white/5 flex items-center justify-between shrink-0">
                <span className="text-xs font-bold text-gray-200 tracking-tight font-display">{STAGE_LABELS[stage]}</span>
                <span className="px-2 py-0.5 bg-white/5 text-gray-400 rounded-full text-[10px] font-bold font-mono">
                  {stageCandidates.length}
                </span>
              </div>

              {/* Card List */}
              <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
                {stageCandidates.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center p-4">
                    <div className="w-10 h-10 rounded-full bg-white/2 flex items-center justify-center text-gray-600 mb-2 font-display">∅</div>
                    <span className="text-[10px] text-gray-500 font-mono">No candidates</span>
                  </div>
                ) : (
                  stageCandidates.map((c) => {
                    const verifiedCount = c.credentials.filter(cr => cr.status === 'verified').length;
                    return (
                      <div
                        key={c.id}
                        onClick={() => onSelectCandidate(c)}
                        className="p-3 bg-[#04080E] border border-white/5 hover:border-[#00BAC8]/40 hover:bg-[#080D15]/60 rounded-lg cursor-pointer transition-all space-y-2 group shadow-sm shadow-black/20"
                      >
                        <div className="flex items-center justify-between gap-1">
                          <span className="text-xs font-bold text-gray-200 group-hover:text-[#00BAC8] transition-colors truncate">{c.name}</span>
                          <span className={`px-1.5 py-0.5 text-[8px] font-bold rounded uppercase border ${ROLE_COLORS[c.role]} font-mono`}>
                            {c.role}
                          </span>
                        </div>

                        <div className="space-y-1 text-[10px] text-gray-400 font-mono">
                          <div className="flex items-center gap-1.5 truncate">
                            <MapPin className="w-3 h-3 text-gray-500 shrink-0" />
                            <span>{c.borough}</span>
                          </div>
                          <div className="flex items-center gap-1.5 truncate">
                            <Phone className="w-3 h-3 text-gray-500 shrink-0" />
                            <span>{c.phone}</span>
                          </div>
                        </div>

                        {/* Audited Status Mini indicators */}
                        <div className="flex items-center justify-between border-t border-white/5 pt-2 mt-2">
                          <div className="flex items-center gap-1 text-[9px] text-gray-500 font-mono">
                            <span>Audited:</span>
                            <span className={verifiedCount === 11 ? 'text-[#00E676] font-bold' : verifiedCount >= 9 ? 'text-[#EFB01F]' : 'text-gray-400'}>
                              {verifiedCount}/11
                            </span>
                          </div>
                          {verifiedCount === 11 ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-[#00E676] shrink-0" />
                          ) : verifiedCount >= 9 ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-[#EFB01F] shrink-0" />
                          ) : (
                            <ShieldAlert className="w-3.5 h-3.5 text-gray-500 shrink-0" />
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Candidate Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-[#0B121C] border border-white/10 rounded-xl overflow-hidden shadow-2xl">
            <div className="p-4 bg-[#080D15] border-b border-white/5 flex items-center justify-between">
              <h3 className="text-sm font-bold font-display text-white">Add Candidate Intake Profile</h3>
              <button 
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-white text-xs font-mono"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleFormSubmit} className="p-6 space-y-4">
              <div>
                <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Full Name</label>
                <input 
                  type="text" 
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Marcus Aurelius"
                  className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Mobile Phone (TCPA)</label>
                  <input 
                    type="tel" 
                    required
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="+15551234567"
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Email Address</label>
                  <input 
                    type="email" 
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="name@example.com"
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Professional Role</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value as CandidateRole })}
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                  >
                    <option value="CNA">CNA (Certified Nursing Assistant)</option>
                    <option value="LPN">LPN (Licensed Practical Nurse)</option>
                    <option value="RN">RN (Registered Nurse)</option>
                  </select>
                </div>
                <div>
                  <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">NYC Borough</label>
                  <select
                    value={formData.borough}
                    onChange={(e) => setFormData({ ...formData, borough: e.target.value as Candidate['borough'] })}
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                  >
                    <option value="Brooklyn">Brooklyn</option>
                    <option value="Bronx">Bronx</option>
                    <option value="Manhattan">Manhattan</option>
                    <option value="Queens">Queens</option>
                    <option value="Staten Island">Staten Island</option>
                  </select>
                </div>
              </div>

              <div className="p-4 bg-yellow-500/5 border border-yellow-500/20 rounded-lg text-[10px] text-gray-400 leading-relaxed">
                <strong>TCPA Disclosure:</strong> Creating this candidate profile simulates capturing an application. Dylan will auto-check permanent opt-outs. If clean, a welcome SMS flow will trigger.
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-white/10 hover:bg-white/5 text-gray-300 text-xs rounded-lg font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-[#00BAC8] text-[#04080E] text-xs rounded-lg font-bold hover:opacity-95 disabled:opacity-50"
                >
                  {loading ? 'Adding...' : 'Verify & Ingest'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
