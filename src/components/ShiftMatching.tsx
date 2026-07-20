import React, { useState, useEffect } from 'react';
import { Shift, Candidate } from '../types';
import { Calendar, Building, MapPin, BadgeDollarSign, Sparkles, Plus, AlertCircle, CheckCircle2, ShieldCheck, DollarSign } from 'lucide-react';
import { CLIENTS_REGISTRY, ClientCenter } from '../clientsData';

interface ShiftMatchingProps {
  shifts: Shift[];
  candidates: Candidate[];
  onAddShift: (shiftData: {
    facility: string;
    role: Candidate['role'];
    borough: Candidate['borough'];
    timeSlot: Shift['timeSlot'];
    hourlyRate: number;
  }) => Promise<void>;
  onMatchShift: (shiftId: string, candidateId: string) => Promise<void>;
}

export default function ShiftMatching({ shifts, candidates, onAddShift, onMatchShift }: ShiftMatchingProps) {
  const [selectedShift, setSelectedShift] = useState<Shift | null>(null);
  const [showAddShiftModal, setShowAddShiftModal] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Client selection state - defaults to BlueLine
  const [activeClientId, setActiveClientId] = useState('blueline');
  const activeClient = CLIENTS_REGISTRY.find(c => c.id === activeClientId) || CLIENTS_REGISTRY[0];

  const [formData, setFormData] = useState({
    facilityId: '',
    facility: '',
    role: 'CNA' as Candidate['role'],
    borough: 'Brooklyn' as Candidate['borough'],
    timeSlot: 'AM' as Shift['timeSlot'],
    hourlyRate: 30
  });

  // Automatically update rates and borough when role or facility changes
  useEffect(() => {
    if (formData.facilityId) {
      const selectedCenter = activeClient.centers.find(c => c.id === formData.facilityId);
      if (selectedCenter) {
        const rate = selectedCenter.rates[formData.role] || selectedCenter.rates['RN'] || 30;
        setFormData(prev => ({
          ...prev,
          facility: selectedCenter.name,
          borough: selectedCenter.borough as any,
          hourlyRate: rate
        }));
      }
    }
  }, [formData.facilityId, formData.role, activeClientId]);

  // Calculate matching candidates for a shift
  const getMatchingCandidates = (shift: Shift) => {
    return candidates.filter(cand => {
      const isRoleMatch = cand.role === shift.role;
      const isBoroughMatch = cand.borough === shift.borough;
      const isAudited = cand.status === 'Audited';
      const isNotOptedOut = !cand.optedOut;
      return isRoleMatch && isBoroughMatch && isAudited && isNotOptedOut;
    });
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.facility || !formData.hourlyRate) return;

    setLoading(true);
    try {
      await onAddShift({
        facility: formData.facility,
        role: formData.role,
        borough: formData.borough,
        timeSlot: formData.timeSlot,
        hourlyRate: formData.hourlyRate
      });
      setShowAddShiftModal(false);
      setFormData({
        facilityId: '',
        facility: '',
        role: 'CNA',
        borough: 'Brooklyn',
        timeSlot: 'AM',
        hourlyRate: 30
      });
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleMatchConfirm = async (candidateId: string) => {
    if (!selectedShift) return;
    setLoading(true);
    try {
      await onMatchShift(selectedShift.id, candidateId);
      setSelectedShift(null);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Active Client Selection Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-[#0B121C] border border-white/5 p-4 rounded-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#00BAC8]/10 border border-[#00BAC8]/30 flex items-center justify-center font-bold text-[#00BAC8]">
            <Building className="w-5 h-5 text-[#00BAC8]" />
          </div>
          <div>
            <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider font-mono block">Tenant Client Registry</span>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white">{activeClient.name}</h2>
              <span className="px-1.5 py-0.5 bg-[#00BAC8]/10 text-[#00BAC8] text-[9px] rounded font-mono uppercase font-bold">Contract Live</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400 font-mono">Switch Client Database:</span>
          <select
            value={activeClientId}
            onChange={(e) => {
              setActiveClientId(e.target.value);
              setSelectedShift(null);
              setFormData({
                facilityId: '',
                facility: '',
                role: 'CNA',
                borough: 'Brooklyn',
                timeSlot: 'AM',
                hourlyRate: 30
              });
            }}
            className="bg-[#04080E] border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#00BAC8] font-mono cursor-pointer"
          >
            {CLIENTS_REGISTRY.map(cl => (
              <option key={cl.id} value={cl.id}>{cl.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left List of Shifts */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between bg-[#0B121C] border border-white/5 p-4 rounded-xl">
            <div className="space-y-0.5">
              <h3 className="text-sm font-bold text-white font-display">NYC Facilities Schedule</h3>
              <p className="text-[10px] text-gray-400 font-mono">Manage open slots and dispatch nurse pairs for {activeClient.name}</p>
            </div>
            <button
              onClick={() => setShowAddShiftModal(true)}
              className="px-3 py-1.5 bg-[#00BAC8]/10 hover:bg-[#00BAC8]/20 border border-[#00BAC8]/30 hover:border-[#00BAC8] text-[#00BAC8] font-bold text-[11px] rounded-lg flex items-center gap-1.5 transition-all"
            >
              <Plus className="w-3.5 h-3.5" /> Post Shift
            </button>
          </div>

          <div className="space-y-3">
            {shifts.map((shift) => {
              const matchesCount = getMatchingCandidates(shift).length;
              const matchedCandidate = candidates.find(c => c.id === shift.matchedCandidateId);
              const isSelected = selectedShift?.id === shift.id;

              return (
                <div
                  key={shift.id}
                  onClick={() => setSelectedShift(shift)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected 
                      ? 'bg-[#00BAC8]/5 border-[#00BAC8]' 
                      : 'bg-[#0B121C] border-white/5 hover:border-white/10'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2">
                        <Building className="w-4 h-4 text-gray-500 shrink-0" />
                        <span className="text-xs font-bold text-gray-200">{shift.facility}</span>
                      </div>

                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-gray-400 font-mono">
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5 text-gray-600" />
                          <span>{shift.borough}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5 text-gray-600" />
                          <span>{shift.timeSlot} Shift ({shift.date})</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="text-[#00E676] font-bold">${shift.hourlyRate}/hr</span>
                        </div>
                      </div>
                    </div>

                    <div className="shrink-0 flex items-center sm:flex-col sm:items-end justify-between gap-1 mt-2 sm:mt-0">
                      <span className={`px-2 py-0.5 text-[9px] font-bold rounded uppercase font-mono ${
                        shift.role === 'CNA' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                        shift.role === 'LPN' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' :
                        'bg-[#00BAC8]/10 text-[#00BAC8] border border-[#00BAC8]/20'
                      }`}>
                        {shift.role} REQUIRED
                      </span>

                      <div className="mt-1">
                        {shift.status === 'Matched' ? (
                          <span className="text-[10px] text-[#00E676] font-bold flex items-center gap-1 font-mono">
                            <CheckCircle2 className="w-3.5 h-3.5 shrink-0" /> Matched: {matchedCandidate?.name.split(' ')[0]}
                          </span>
                        ) : matchesCount > 0 ? (
                          <span className="px-1.5 py-0.5 bg-[#00BAC8]/10 border border-[#00BAC8]/20 text-[#00BAC8] rounded text-[9px] font-mono font-bold animate-pulse">
                            🔥 {matchesCount} MATCHES READY
                          </span>
                        ) : (
                          <span className="text-[10px] text-gray-500 font-mono">No compliant match</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Matrix Workspace */}
        <div className="lg:col-span-5">
          {selectedShift ? (
            <div className="bg-[#0B121C] border border-white/5 rounded-xl p-5 space-y-6">
              <div className="border-b border-white/5 pb-4 space-y-1.5">
                <span className="text-[10px] text-[#00BAC8] font-bold font-mono uppercase tracking-wider block">Selected Shift Detail</span>
                <h3 className="text-sm font-bold text-gray-200">{selectedShift.facility}</h3>
                <p className="text-[11px] text-gray-400 font-mono">
                  Matching {selectedShift.role}s in {selectedShift.borough}
                </p>
              </div>

              {selectedShift.status === 'Matched' ? (
                <div className="bg-[#04080E]/60 border border-[#00E676]/20 p-4 rounded-xl text-center space-y-3">
                  <CheckCircle2 className="w-8 h-8 text-[#00E676] mx-auto shrink-0" />
                  <h4 className="text-xs font-bold text-gray-200">Shift Filled &amp; Alerted</h4>
                  <p className="text-[11px] text-gray-400 font-mono max-w-xs mx-auto">
                    Matched candidate ({candidates.find(c => c.id === selectedShift.matchedCandidateId)?.name}) was notified. Compliance audit is locked for this shift.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-xs text-[#00BAC8] font-semibold bg-[#00BAC8]/10 px-3 py-2 rounded-lg border border-[#00BAC8]/20">
                    <Sparkles className="w-4 h-4 shrink-0" />
                    <span>Dylan AI Auto-Match Algorithm</span>
                  </div>

                  <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                    {getMatchingCandidates(selectedShift).length === 0 ? (
                      <div className="p-6 bg-[#04080E]/40 border border-white/5 rounded-xl text-center space-y-2">
                        <AlertCircle className="w-6 h-6 text-[#EFB01F] mx-auto shrink-0" />
                        <span className="text-xs font-bold text-gray-300 block">No Fully Compliant Match Found</span>
                        <p className="text-[10px] text-gray-400 font-sans">
                          Requires candidates in <strong>{selectedShift.borough}</strong> with <strong>{selectedShift.role}</strong> credentials fully verified (status: "Audited"). Run the daily cron to update folders.
                        </p>
                      </div>
                    ) : (
                      getMatchingCandidates(selectedShift).map((cand) => (
                        <div
                          key={cand.id}
                          className="p-3 bg-[#04080E] border border-white/5 hover:border-[#00BAC8]/20 rounded-lg flex items-center justify-between gap-3 group"
                        >
                          <div className="truncate">
                            <span className="text-xs font-bold text-gray-200 group-hover:text-[#00BAC8] transition-colors block truncate">{cand.name}</span>
                            <span className="text-[9px] text-gray-500 font-mono block">Applied: {new Date(cand.appliedDate).toLocaleDateString()}</span>
                          </div>
                          <button
                            onClick={() => handleMatchConfirm(cand.id)}
                            disabled={loading}
                            className="px-3 py-1.5 bg-[#00BAC8] hover:opacity-90 text-[#04080E] font-extrabold text-[10px] rounded font-mono uppercase shrink-0"
                          >
                            Pair &amp; Alert
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full bg-[#0B121C] border border-white/5 rounded-xl p-8 flex flex-col items-center justify-center text-center text-gray-500">
              <Building className="w-12 h-12 text-gray-700 mb-3" />
              <span className="text-xs font-medium">Select a posted facility shift from the roster to deploy matching algorithms.</span>
            </div>
          )}
        </div>
      </div>

      {/* Contract Rate Matrix Table Reference */}
      <div className="bg-[#0B121C] border border-white/5 rounded-xl p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/5 pb-4">
          <div>
            <h3 className="text-xs font-bold text-white font-display uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-[#00BAC8]" />
              {activeClient.name} contracted hourly rates by center
            </h3>
            <p className="text-[10px] text-gray-400 font-mono mt-0.5">Reference panel populated with direct contract terms</p>
          </div>
          <div className="text-[10px] text-gray-400 font-mono flex gap-4">
            <div>Support Email: <span className="text-white">{activeClient.supportEmail}</span></div>
            <div>Support Phone: <span className="text-white">{activeClient.supportPhone}</span></div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-[11px] font-mono">
            <thead>
              <tr className="border-b border-white/5 text-gray-400">
                <th className="py-2 font-bold uppercase text-[9px]">Center Name</th>
                <th className="py-2 font-bold uppercase text-[9px]">Borough</th>
                <th className="py-2 font-bold uppercase text-[9px] text-[#00BAC8]">CNA Rate</th>
                <th className="py-2 font-bold uppercase text-[9px] text-purple-400">LPN Rate</th>
                <th className="py-2 font-bold uppercase text-[9px] text-blue-400">RN Rate</th>
                <th className="py-2 font-bold uppercase text-[9px] text-emerald-400">RNS Rate</th>
                <th className="py-2 font-bold uppercase text-[9px] text-gray-400">Contact / Email</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/2">
              {activeClient.centers.map((center) => (
                <tr key={center.id} className="hover:bg-white/2 transition-colors">
                  <td className="py-2.5 font-bold text-gray-200">{center.name}</td>
                  <td className="py-2.5 text-gray-400">{center.borough}</td>
                  <td className="py-2.5 font-bold text-[#00BAC8]">${center.rates.CNA}/hr</td>
                  <td className="py-2.5 font-bold text-purple-400">${center.rates.LPN}/hr</td>
                  <td className="py-2.5 font-bold text-blue-400">${center.rates.RN}/hr</td>
                  <td className="py-2.5 text-emerald-400 font-medium">
                    {center.rates.RNS ? `$${center.rates.RNS}/hr` : '—'}
                  </td>
                  <td className="py-2.5 text-gray-500 truncate max-w-[200px]" title={`${center.contact || ''} - ${center.email || ''}`}>
                    {center.contact ? `${center.contact} (${center.email})` : 'No contact on file'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Post Shift Modal */}
      {showAddShiftModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="w-full max-w-sm bg-[#0B121C] border border-white/10 rounded-xl overflow-hidden shadow-2xl">
            <div className="p-4 bg-[#080D15] border-b border-white/5 flex items-center justify-between">
              <h3 className="text-sm font-bold font-display text-white">Post Facility Shift ({activeClient.name})</h3>
              <button 
                onClick={() => setShowAddShiftModal(false)}
                className="text-gray-400 hover:text-white text-xs font-mono"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleFormSubmit} className="p-6 space-y-4">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block">Facility Name</label>
                  <button
                    type="button"
                    onClick={() => {
                      setFormData(prev => ({
                        ...prev,
                        facilityId: prev.facilityId === 'custom' ? '' : 'custom',
                        facility: '',
                        hourlyRate: 30
                      }));
                    }}
                    className="text-[9px] text-[#00BAC8] font-mono hover:underline"
                  >
                    {formData.facilityId === 'custom' ? 'Select from registry' : 'Enter custom center'}
                  </button>
                </div>
                
                {formData.facilityId === 'custom' ? (
                  <input 
                    type="text" 
                    required
                    value={formData.facility}
                    onChange={(e) => setFormData({ ...formData, facility: e.target.value })}
                    placeholder="e.g. Bronx Park Rehabilitation Center"
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                  />
                ) : (
                  <select
                    required
                    value={formData.facilityId}
                    onChange={(e) => setFormData({ ...formData, facilityId: e.target.value })}
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                  >
                    <option value="">-- Select {activeClient.name} Center --</option>
                    {activeClient.centers.map(center => (
                      <option key={center.id} value={center.id}>
                        {center.name} ({center.borough})
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Required Role</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value as Candidate['role'] })}
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                  >
                    <option value="CNA">CNA</option>
                    <option value="LPN">LPN</option>
                    <option value="RN">RN</option>
                  </select>
                </div>
                <div>
                  <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Borough</label>
                  <select
                    value={formData.borough}
                    onChange={(e) => setFormData({ ...formData, borough: e.target.value as Candidate['borough'] })}
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                    disabled={formData.facilityId !== 'custom' && formData.facilityId !== ''}
                  >
                    <option value="Brooklyn">Brooklyn</option>
                    <option value="Bronx">Bronx</option>
                    <option value="Manhattan">Manhattan</option>
                    <option value="Queens">Queens</option>
                    <option value="Staten Island">Staten Island</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">
                    Hourly Rate ($) {formData.facilityId && formData.facilityId !== 'custom' && '(Contracted)'}
                  </label>
                  <div className="relative">
                    <span className="absolute left-2.5 top-2.5 text-gray-500 text-[10px] font-bold font-mono">$</span>
                    <input 
                      type="number"
                      required
                      value={formData.hourlyRate}
                      onChange={(e) => setFormData({ ...formData, hourlyRate: Number(e.target.value) })}
                      className="w-full bg-[#04080E] border border-white/10 rounded-lg pl-6 pr-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Time Slot</label>
                  <select
                    value={formData.timeSlot}
                    onChange={(e) => setFormData({ ...formData, timeSlot: e.target.value as Shift['timeSlot'] })}
                    className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                  >
                    <option value="AM">AM Shift</option>
                    <option value="PM">PM Shift</option>
                    <option value="Overnight">Overnight</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowAddShiftModal(false)}
                  className="px-4 py-2 border border-white/10 hover:bg-white/5 text-gray-300 text-xs rounded-lg font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-[#00BAC8] text-[#04080E] text-xs rounded-lg font-bold hover:opacity-95 disabled:opacity-50"
                >
                  {loading ? 'Posting...' : 'Post Shift'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
