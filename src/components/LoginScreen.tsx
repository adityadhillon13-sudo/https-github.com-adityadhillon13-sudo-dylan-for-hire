import React, { useState, useEffect } from 'react';
import { Lock, User, Sparkles, Building, ArrowRight, ShieldCheck, Eye, EyeOff } from 'lucide-react';

interface LoginScreenProps {
  onLogin: (role: 'admin' | 'client') => void;
  defaultRole?: 'admin' | 'client';
}

export default function LoginScreen({ onLogin, defaultRole = 'admin' }: LoginScreenProps) {
  const [username, setUsername] = useState(defaultRole === 'admin' ? 'dylanforhire' : 'blueline');
  const [password, setPassword] = useState('password');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setUsername(defaultRole === 'admin' ? 'dylanforhire' : 'blueline');
    setPassword('password');
  }, [defaultRole]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    setTimeout(() => {
      const cleanUser = username.trim().toLowerCase();
      
      if (cleanUser === 'dylanforhire' && password === 'password') {
        onLogin('admin');
      } else if (cleanUser === 'blueline' && password === 'password') {
        onLogin('client');
      } else {
        setError('Invalid username or password. Try auto-fill buttons below!');
        setLoading(false);
      }
    }, 600);
  };

  const handleAutoFill = (role: 'admin' | 'client') => {
    if (role === 'admin') {
      setUsername('dylanforhire');
      setPassword('password');
    } else {
      setUsername('blueline');
      setPassword('password');
    }
    setError('');
  };

  return (
    <div className="min-h-screen bg-[#04080E] text-white flex flex-col justify-between selection:bg-[#00BAC8]/30 relative overflow-hidden">
      {/* Decorative Blur Spheres */}
      <div className="absolute top-[-10%] left-[-10%] w-[40rem] h-[40rem] bg-[#00BAC8]/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[35rem] h-[35rem] bg-[#9C27B0]/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <header className="border-b border-white/5 h-16 flex items-center justify-between px-6 bg-[#080D15]/80 backdrop-blur z-10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-[#00BAC8]/10 border border-[#00BAC8] flex items-center justify-center font-bold text-lg text-[#00BAC8] font-display">D</div>
          <span className="font-bold text-lg tracking-wider font-display">DYLAN <span className="text-[#00BAC8]">FOR HIRE</span></span>
        </div>
        <span className="text-xs font-mono text-gray-500">v3.0 Secure Auth Gate</span>
      </header>

      {/* Main Form Center */}
      <div className="flex-1 flex items-center justify-center p-6 z-10">
        <div className="w-full max-w-md bg-[#0B121C] border border-white/10 rounded-2xl p-8 space-y-6 shadow-2xl shadow-black/80">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 bg-[#00BAC8]/10 border border-[#00BAC8]/30 rounded-xl flex items-center justify-center mx-auto text-[#00BAC8]">
              <Lock className="w-6 h-6 animate-pulse" />
            </div>
            <h2 className="text-xl font-bold tracking-tight text-white font-display">Log in to Dylan for Hire</h2>
            <p className="text-xs text-gray-400">
              Access the AI-powered Nurse Staffing back-office workspace and automation pipelines.
            </p>
          </div>

          {error && (
            <div className="p-3 bg-[#F04040]/10 border border-[#F04040]/30 rounded-lg text-xs text-[#F04040] text-center font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username */}
            <div className="space-y-1.5">
              <label className="text-[10px] uppercase tracking-wider text-gray-400 font-bold font-mono">Username</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-gray-500">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  required
                  placeholder="e.g. dylanforhire or blueline"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-[#04080E] border border-white/10 rounded-lg py-2.5 pl-10 pr-4 text-xs text-white focus:outline-none focus:border-[#00BAC8] transition-colors"
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label className="text-[10px] uppercase tracking-wider text-gray-400 font-bold font-mono">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-gray-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#04080E] border border-white/10 rounded-lg py-2.5 pl-10 pr-10 text-xs text-white focus:outline-none focus:border-[#00BAC8] transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-3 flex items-center text-gray-500 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-[#00BAC8] text-[#04080E] font-bold text-xs rounded-lg hover:opacity-95 transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-[#04080E]/20 border-t-[#04080E] rounded-full animate-spin" />
              ) : (
                <>
                  <span>Sign In Securely</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          {/* Sandbox Presets - Interactive helper */}
          <div className="border-t border-white/5 pt-5 space-y-3">
            <span className="text-[10px] uppercase tracking-wider text-gray-500 font-bold font-mono block text-center">
              DEMO GATEWAY PRESETS
            </span>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  handleAutoFill('admin');
                  handleSubmit({ preventDefault: () => {} } as any);
                }}
                className="p-3 bg-[#0c1a29] border border-[#00BAC8]/30 rounded-xl text-left hover:border-[#00BAC8] hover:bg-[#0f2237] transition-all space-y-1 group"
              >
                <div className="flex items-center gap-1.5 text-[10px] font-bold text-[#00BAC8] uppercase font-mono">
                  <ShieldCheck className="w-3.5 h-3.5" /> Dylan Admin
                </div>
                <p className="text-[9px] text-gray-400 group-hover:text-white leading-normal">
                  Full operator view with all client tabs and tenant onboarding.
                </p>
              </button>

              <button
                type="button"
                onClick={() => {
                  handleAutoFill('client');
                  handleSubmit({ preventDefault: () => {} } as any);
                }}
                className="p-3 bg-[#110f21] border border-[#9C27B0]/30 rounded-xl text-left hover:border-[#9C27B0] hover:bg-[#18152e] transition-all space-y-1 group"
              >
                <div className="flex items-center gap-1.5 text-[10px] font-bold text-[#D500F9] uppercase font-mono">
                  <Building className="w-3.5 h-3.5" /> BlueLine Client
                </div>
                <p className="text-[9px] text-gray-400 group-hover:text-white leading-normal">
                  Restricted tenant context showing only BlueLine data.
                </p>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer credits */}
      <footer className="py-4 border-t border-white/5 text-center text-[10px] text-gray-600 font-mono">
        © 2026 Dylan for Hire Inc. All data and connections are mock-audited live in real-time.
      </footer>
    </div>
  );
}
