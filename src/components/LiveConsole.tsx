import React, { useState } from 'react';
import { LogEntry } from '../types';
import { Terminal, Trash2, Play, AlertCircle, CheckCircle, Info, RefreshCw } from 'lucide-react';

interface LiveConsoleProps {
  logs: LogEntry[];
  onTriggerDailyCron: () => Promise<void>;
  onClearConsole: () => Promise<void>;
}

export default function LiveConsole({ logs, onTriggerDailyCron, onClearConsole }: LiveConsoleProps) {
  const [filter, setFilter] = useState<'ALL' | 'INFO' | 'SUCCESS' | 'WARN'>('ALL');
  const [running, setRunning] = useState(false);

  const handleTrigger = async () => {
    setRunning(true);
    try {
      await onTriggerDailyCron();
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filter === 'ALL') return true;
    return log.level.toUpperCase() === filter;
  });

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'success': return 'text-[#00E676]';
      case 'warn': return 'text-[#EFB01F] font-bold animate-pulse';
      case 'info': return 'text-[#00BAC8]';
      default: return 'text-gray-400';
    }
  };

  const getLevelIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'success': return <CheckCircle className="w-3.5 h-3.5 text-[#00E676] shrink-0" />;
      case 'warn': return <AlertCircle className="w-3.5 h-3.5 text-[#EFB01F] shrink-0" />;
      case 'info': return <Info className="w-3.5 h-3.5 text-[#00BAC8] shrink-0" />;
      default: return null;
    }
  };

  return (
    <div className="bg-[#0B121C] border border-white/5 rounded-xl overflow-hidden flex flex-col h-[520px] shadow-2xl">
      {/* Console actions */}
      <div className="p-4 bg-[#080D15] border-b border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-[#00BAC8]" />
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider font-display">Dylan Orchestrator Terminal</h3>
            <span className="text-[10px] text-gray-400 font-mono">Live Pub/Sub event logs and automation cycles</span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Level Filter */}
          <div className="flex items-center gap-1 bg-[#04080E] border border-white/10 rounded-lg p-0.5">
            {['ALL', 'INFO', 'SUCCESS', 'WARN'].map((lvl) => (
              <button
                key={lvl}
                onClick={() => setFilter(lvl as any)}
                className={`px-2 py-1 text-[9px] font-bold rounded uppercase transition-all ${
                  filter === lvl 
                    ? 'bg-[#00BAC8]/10 border border-[#00BAC8]/30 text-[#00BAC8]' 
                    : 'text-gray-500 hover:text-white'
                }`}
              >
                {lvl}
              </button>
            ))}
          </div>

          <button
            onClick={onClearConsole}
            className="p-2 border border-white/10 hover:bg-white/5 text-gray-400 hover:text-[#F04040] rounded-lg transition-colors"
            title="Clear Console"
          >
            <Trash2 className="w-4 h-4" />
          </button>

          <button
            onClick={handleTrigger}
            disabled={running}
            className="px-4 py-2 bg-[#00E676] hover:bg-[#00E676]/90 text-[#04080E] font-extrabold text-xs rounded-lg flex items-center gap-1.5 transition-all shadow-lg disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${running ? 'animate-spin' : ''}`} />
            {running ? 'Executing...' : 'Trigger Daily Cycle'}
          </button>
        </div>
      </div>

      {/* Terminal Display */}
      <div className="flex-1 bg-[#04080E] p-4 font-mono text-[11px] leading-relaxed overflow-y-auto space-y-2">
        <div className="p-3 bg-white/5 border border-white/5 rounded-lg text-gray-400 mb-4 leading-normal">
          <span className="text-[#00BAC8] font-bold block mb-1">💡 Simulation Helper:</span>
          Click <strong>Trigger Daily Cycle</strong> to simulate Dylan's daily orchestrations. It parses incoming folders (Intake), runs automated 11-point credential audits (Captured), matches candidates (Audited), and triggers facility matches.
        </div>

        {filteredLogs.length === 0 ? (
          <div className="h-48 flex items-center justify-center text-gray-600 italic">
            Console stream empty.
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div key={log.id} className="flex items-start gap-2 py-1 border-b border-white/2 hover:bg-white/2 rounded px-1 transition-colors">
              <span className="text-gray-600 shrink-0 select-none">
                [{new Date(log.timestamp).toISOString().substring(11, 19)}]
              </span>
              <span className="shrink-0 font-bold uppercase select-none text-[9px] w-14">
                [{log.service.split('_')[0]}]
              </span>
              {getLevelIcon(log.level)}
              <span className={`flex-1 break-all ${getLevelColor(log.level)}`}>
                {log.message}
              </span>
            </div>
          ))
        )}
      </div>

      {/* System Status Footer */}
      <div className="p-2.5 bg-[#080D15] border-t border-white/5 flex items-center justify-between text-[10px] text-gray-500 font-mono shrink-0">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[#00E676] animate-pulse"></span>
          <span>Websocket Connection: Secured</span>
        </div>
        <span>Dylan AI Engine v3.0 stable</span>
      </div>
    </div>
  );
}
