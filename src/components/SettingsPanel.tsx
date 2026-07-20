import React, { useState } from 'react';
import { SystemSettings } from '../types';
import { Settings, ShieldCheck, Mail, Phone, Sliders, Users, Trash, Plus, Check } from 'lucide-react';

interface SettingsPanelProps {
  settings: SystemSettings;
  blacklist: string[];
  onUpdateSettings: (newSettings: SystemSettings) => Promise<void>;
  onAddBlacklist: (phone: string) => Promise<void>;
}

export default function SettingsPanel({ settings, blacklist, onUpdateSettings, onAddBlacklist }: SettingsPanelProps) {
  const [formData, setFormData] = useState<SystemSettings>({ ...settings });
  const [newBlacklistPhone, setNewBlacklistPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSettingsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onUpdateSettings(formData);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2000);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddBlacklist = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBlacklistPhone) return;
    setLoading(true);
    try {
      await onAddBlacklist(newBlacklistPhone);
      setNewBlacklistPhone('');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* Left: General settings */}
      <div className="lg:col-span-7 bg-[#0B121C] border border-white/5 rounded-xl p-6">
        <div className="flex items-center gap-2 mb-6 border-b border-white/5 pb-4">
          <Settings className="w-5 h-5 text-[#00BAC8]" />
          <div>
            <h3 className="text-sm font-bold text-white font-display">System Configuration</h3>
            <p className="text-[10px] text-gray-400 font-mono">Customize agency parameters and automation rules</p>
          </div>
        </div>

        <form onSubmit={handleSettingsSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Agency Name</label>
              <input 
                type="text"
                required
                value={formData.agencyName}
                onChange={(e) => setFormData({ ...formData, agencyName: e.target.value })}
                className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
              />
            </div>
            <div>
              <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Dylan Outbound Phone (OpenPhone)</label>
              <input 
                type="text"
                required
                value={formData.openPhoneLine}
                onChange={(e) => setFormData({ ...formData, openPhoneLine: e.target.value })}
                className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Intake Support Phone</label>
              <input 
                type="text"
                required
                value={formData.supportPhone}
                onChange={(e) => setFormData({ ...formData, supportPhone: e.target.value })}
                className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
              />
            </div>
            <div>
              <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Intake Support Email</label>
              <input 
                type="email"
                required
                value={formData.supportEmail}
                onChange={(e) => setFormData({ ...formData, supportEmail: e.target.value })}
                className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
              />
            </div>
          </div>

          <div>
            <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Auto-Match Similarity Threshold</label>
            <div className="flex items-center gap-3">
              <input 
                type="range"
                min="0.5"
                max="0.95"
                step="0.05"
                value={formData.autoMatchThreshold}
                onChange={(e) => setFormData({ ...formData, autoMatchThreshold: Number(e.target.value) })}
                className="flex-1 accent-[#00BAC8] bg-[#04080E] h-2 rounded-lg cursor-pointer"
              />
              <span className="text-xs text-[#00BAC8] font-bold font-mono">{(formData.autoMatchThreshold * 100).toFixed(0)}%</span>
            </div>
            <p className="text-[9px] text-gray-500 mt-1">Lower threshold will accept broader geographical matches in NYC.</p>
          </div>

          <div>
            <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Opt-Out Keywords (SMS trigger)</label>
            <div className="flex flex-wrap gap-1 mt-1.5">
              {formData.optOutKeywords.map((keyword, i) => (
                <span key={i} className="px-2 py-1 bg-[#F04040]/10 border border-[#F04040]/20 text-[#F04040] text-[9px] font-bold font-mono rounded">
                  {keyword}
                </span>
              ))}
            </div>
            <p className="text-[9px] text-gray-500 mt-1">Ironclad. Inbound texts containing these keywords automatically blacklist numbers.</p>
          </div>

          <div className="flex items-center justify-between border-t border-white/5 pt-4 mt-6">
            {savedSuccess ? (
              <span className="text-xs text-[#00E676] font-mono flex items-center gap-1">
                <Check className="w-4 h-4" /> Parameters saved successfully
              </span>
            ) : <div />}
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 bg-[#00BAC8] hover:opacity-95 text-[#04080E] text-xs font-bold rounded-lg transition-all"
            >
              Save Parameters
            </button>
          </div>
        </form>
      </div>

      {/* Right: Permanent Blacklist registry */}
      <div className="lg:col-span-5 bg-[#0B121C] border border-white/5 rounded-xl p-6 flex flex-col justify-between">
        <div className="space-y-4">
          <div className="flex items-center gap-2 border-b border-white/5 pb-4">
            <Sliders className="w-5 h-5 text-[#F04040]" />
            <div>
              <h3 className="text-sm font-bold text-white font-display">Permanent Blacklist</h3>
              <p className="text-[10px] text-gray-400 font-mono">Synchronized 100% compliant TCPA registry</p>
            </div>
          </div>

          <form onSubmit={handleAddBlacklist} className="flex gap-2">
            <input 
              type="tel"
              required
              placeholder="Blacklist number (e.g. +15551112233)"
              value={newBlacklistPhone}
              onChange={(e) => setNewBlacklistPhone(e.target.value)}
              className="flex-1 bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-3.5 py-2 bg-[#F04040] hover:opacity-90 text-white text-xs font-bold rounded-lg transition-all shrink-0 flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Blacklist
            </button>
          </form>

          <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
            {blacklist.length === 0 ? (
              <div className="text-center py-6 text-gray-500 font-mono text-xs">
                Registry is empty.
              </div>
            ) : (
              blacklist.map((phone, i) => (
                <div key={i} className="p-2.5 bg-[#04080E] border border-white/5 rounded-lg flex items-center justify-between text-xs font-mono text-gray-300">
                  <span>{phone}</span>
                  <span className="text-[9px] font-extrabold uppercase text-[#F04040] bg-[#F04040]/10 border border-[#F04040]/20 px-1.5 py-0.5 rounded">
                    Banned
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="p-4 bg-red-500/5 border border-red-500/20 text-[10px] text-gray-400 leading-relaxed rounded-lg mt-6">
          <strong>TCPA &amp; Rule 07:</strong> Numbers in this registry bypass all workflows. Active campaigns will immediately reject or block any candidates matching these phone numbers.
        </div>
      </div>
    </div>
  );
}
