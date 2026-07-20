import React, { useState } from 'react';
import { Candidate, CredentialStatus } from '../types';
import { ShieldCheck, Calendar, FileText, ArrowRight, CheckCircle2, XCircle, AlertCircle, Sparkles, Upload, FileUp } from 'lucide-react';
import ScannedDocumentViewer from './ScannedDocumentViewer';

interface CredentialAuditProps {
  candidate: Candidate;
  onUpdateCandidate: (updated: Candidate) => Promise<void>;
  onClose: () => void;
}

const SAMPLE_FILES = [
  { name: "nys_registry_cna_lic.pdf", size: "342 KB", match: "NYS Nurse License / Registry ID", note: "Lic #998342, Status: Active" },
  { name: "aha_cpr_bls_card.jpg", size: "1.2 MB", match: "BLS Certification (CPR)", note: "Exp: 11/2027, Provider: AHA" },
  { name: "ppd_skin_test_ppd.pdf", size: "215 KB", match: "TB Test Result (PPD / QuantiFERON)", note: "Result: Negative, Read: 06/2026" },
  { name: "annual_physical_2026.pdf", size: "840 KB", match: "Annual Physical Exam", note: "Cleared for full duty, Exam: 05/2026" },
  { name: "signed_hepb_declination.pdf", size: "118 KB", match: "Hepatitis B Vaccination / Declination", note: "Signed Declination Form submitted" }
];

export default function CredentialAudit({ candidate, onUpdateCandidate, onClose }: CredentialAuditProps) {
  const [selectedCred, setSelectedCred] = useState<CredentialStatus | null>(candidate.credentials[0] || null);
  const [auditing, setAuditing] = useState(false);
  const [visionReport, setVisionReport] = useState<string | null>(null);
  const [manualNote, setManualNote] = useState('');
  const [manualExpiry, setManualExpiry] = useState('');

  const handleRunVisionAudit = async (sampleFile: typeof SAMPLE_FILES[0]) => {
    if (!selectedCred) return;
    setAuditing(true);
    setVisionReport(null);

    try {
      const res = await fetch('/api/verify-document', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fileName: sampleFile.name,
          credentialType: selectedCred.name,
          candidateName: candidate.name
        })
      });
      const data = await res.json();
      setAuditing(false);
      if (data.error) {
        setVisionReport(`[AUDIT FAILED]\nError: ${data.error}`);
        return;
      }
      
      const formattedReport = `[DYLAN AI VISION VERIFICATION REPORT]
File: ${sampleFile.name}
Analyzed Category: ${data.documentType || selectedCred.name}
Extracted Document ID: ${data.documentId || 'N/A'}
Authenticity Score: ${data.authenticityScore}%

OCR Extraction & 11-Pt Verification Checklist:
${data.checklist.map((c: any) => `- [${c.passed ? '✓' : '✗'}] ${c.check}: ${c.details}`).join('\n')}

Auditor Notes:
${data.notes}

Status: ${data.verified ? 'APPROVED & COMPLIANT' : 'REJECTED / OUTSTANDING ACTION REQUIRED'}
Audit Signature: ${data.auditor || 'Dylan-AI-Vision-v3.0'}`;

      setVisionReport(formattedReport);
      
      // Auto-update fields
      setManualExpiry(data.expiryDate || '');
      setManualNote(`Dylan Vision verified. Exp: ${data.expiryDate}. Notes: ${data.notes.slice(0, 80)}...`);
    } catch (err: any) {
      setAuditing(false);
      setVisionReport(`[AUDIT ERROR]\nConnection to verification gateway failed: ${err.message}`);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !selectedCred) return;
    
    setAuditing(true);
    setVisionReport(null);
    
    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64Data = (reader.result as string).split(',')[1];
      try {
        const res = await fetch('/api/verify-document', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            fileName: file.name,
            fileData: base64Data,
            mimeType: file.type,
            credentialType: selectedCred.name,
            candidateName: candidate.name
          })
        });
        const data = await res.json();
        setAuditing(false);
        if (data.error) {
          setVisionReport(`[AUDIT FAILED]\nError: ${data.error}`);
          return;
        }
        
        const formattedReport = `[DYLAN AI VISION VERIFICATION REPORT]
File: ${file.name}
Analyzed Category: ${data.documentType || selectedCred.name}
Extracted Document ID: ${data.documentId || 'N/A'}
Authenticity Score: ${data.authenticityScore}%

OCR Extraction & 11-Pt Verification Checklist:
${data.checklist.map((c: any) => `- [${c.passed ? '✓' : '✗'}] ${c.check}: ${c.details}`).join('\n')}

Auditor Notes:
${data.notes}

Status: ${data.verified ? 'APPROVED & COMPLIANT' : 'REJECTED / OUTSTANDING ACTION REQUIRED'}
Audit Signature: ${data.auditor || 'Dylan-AI-Vision-v3.0'}`;

        setVisionReport(formattedReport);
        setManualExpiry(data.expiryDate || '');
        setManualNote(`Dylan Vision verified. Exp: ${data.expiryDate}. Notes: ${data.notes.slice(0, 80)}...`);
      } catch (err: any) {
        setAuditing(false);
        setVisionReport(`[AUDIT ERROR]\nConnection to verification gateway failed: ${err.message}`);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleSaveCredential = async (status: 'verified' | 'failed') => {
    if (!selectedCred) return;

    const updatedCreds = candidate.credentials.map(cr => {
      if (cr.id === selectedCred.id) {
        return {
          ...cr,
          status,
          expiryDate: manualExpiry || cr.expiryDate,
          notes: manualNote || cr.notes
        };
      }
      return cr;
    });

    const isFullyCompliant = updatedCreds
      .filter(cr => cr.required)
      .every(cr => cr.status === 'verified');

    const updatedCandidate: Candidate = {
      ...candidate,
      credentials: updatedCreds,
      status: isFullyCompliant ? 'Audited' : candidate.status === 'Audited' ? 'Captured' : candidate.status
    };

    await onUpdateCandidate(updatedCandidate);
    setSelectedCred(updatedCandidate.credentials.find(cr => cr.id === selectedCred.id) || null);
    setVisionReport(null);
    setManualNote('');
    setManualExpiry('');
  };

  const requiredCount = candidate.credentials.filter(c => c.required).length;
  const verifiedRequiredCount = candidate.credentials.filter(c => c.required && c.status === 'verified').length;
  const optionalCount = candidate.credentials.filter(c => !c.required).length;
  const verifiedOptionalCount = candidate.credentials.filter(c => !c.required && c.status === 'verified').length;

  return (
    <div className="bg-[#0B121C] border border-white/5 rounded-xl overflow-hidden shadow-2xl h-full flex flex-col">
      {/* Header */}
      <div className="p-4 bg-[#080D15] border-b border-white/5 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-[#00BAC8]" />
          <div>
            <h3 className="text-sm font-bold font-display text-white">{candidate.name}'s Credential Audit</h3>
            <span className="text-[10px] text-gray-400 font-mono">11-Point Compliance Checklist ({candidate.role})</span>
          </div>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-white font-mono text-xs">✕ Close</button>
      </div>

      {/* Grid container */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-12 overflow-hidden">
        {/* Left: Credential Checklist (Line-items) */}
        <div className="md:col-span-5 border-r border-white/5 overflow-y-auto p-4 space-y-4">
          <div>
            <div className="flex justify-between items-center text-[10px] text-gray-400 font-mono uppercase tracking-wider mb-2">
              <span>Required Documents</span>
              <span className="text-[#00BAC8] font-bold">{verifiedRequiredCount}/{requiredCount} verified</span>
            </div>
            <div className="space-y-1.5">
              {candidate.credentials.filter(c => c.required).map(c => (
                <button
                  key={c.id}
                  onClick={() => { setSelectedCred(c); setVisionReport(null); }}
                  className={`w-full text-left p-2.5 rounded-lg border text-xs flex items-center justify-between transition-all ${
                    selectedCred?.id === c.id 
                      ? 'bg-[#00BAC8]/10 border-[#00BAC8] text-[#00BAC8]' 
                      : 'bg-[#04080E]/60 border-white/5 text-gray-300 hover:bg-[#04080E]'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    {c.status === 'verified' && <CheckCircle2 className="w-3.5 h-3.5 text-[#00E676] shrink-0" />}
                    {c.status === 'failed' && <XCircle className="w-3.5 h-3.5 text-[#F04040] shrink-0" />}
                    {c.status === 'pending' && <AlertCircle className="w-3.5 h-3.5 text-[#EFB01F] shrink-0" />}
                    <span className="truncate">{c.name}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center text-[10px] text-gray-400 font-mono uppercase tracking-wider mb-2 pt-2 border-t border-white/5">
              <span>Recommended (Declinations accepted)</span>
              <span className="text-gray-400 font-bold">{verifiedOptionalCount}/{optionalCount} submitted</span>
            </div>
            <div className="space-y-1.5">
              {candidate.credentials.filter(c => !c.required).map(c => (
                <button
                  key={c.id}
                  onClick={() => { setSelectedCred(c); setVisionReport(null); }}
                  className={`w-full text-left p-2.5 rounded-lg border text-xs flex items-center justify-between transition-all ${
                    selectedCred?.id === c.id 
                      ? 'bg-[#00BAC8]/10 border-[#00BAC8] text-[#00BAC8]' 
                      : 'bg-[#04080E]/60 border-white/5 text-gray-300 hover:bg-[#04080E]'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    {c.status === 'verified' && <CheckCircle2 className="w-3.5 h-3.5 text-[#00E676] shrink-0" />}
                    {c.status === 'failed' && <XCircle className="w-3.5 h-3.5 text-[#F04040] shrink-0" />}
                    {c.status === 'pending' && <AlertCircle className="w-3.5 h-3.5 text-gray-500 shrink-0" />}
                    <span className="truncate">{c.name}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Detailed Auditor Workspace */}
        <div className="md:col-span-7 overflow-y-auto p-4 flex flex-col bg-[#04080E]/40">
          {selectedCred ? (
            <div className="space-y-6 flex-1 flex flex-col justify-between">
              {/* Info panel */}
              <div className="space-y-4">
                <div className="flex items-start justify-between bg-[#0B121C] border border-white/5 p-4 rounded-xl">
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5">
                      <h4 className="text-sm font-bold text-gray-200">{selectedCred.name}</h4>
                      <span className={`px-2 py-0.5 rounded text-[8px] font-bold ${selectedCred.required ? 'bg-[#F04040]/10 text-[#F04040] border border-[#F04040]/20' : 'bg-gray-800 text-gray-400'}`}>
                        {selectedCred.required ? 'REQUIRED' : 'RECOMMENDED'}
                      </span>
                    </div>
                    {selectedCred.notes && <p className="text-xs text-[#00BAC8] italic font-mono">{selectedCred.notes}</p>}
                    {selectedCred.expiryDate && (
                      <div className="flex items-center gap-1 text-[10px] text-gray-400 font-mono mt-2">
                        <Calendar className="w-3.5 h-3.5 text-gray-500" />
                        <span>Expiry Date: <strong className="text-gray-200">{selectedCred.expiryDate}</strong></span>
                      </div>
                    )}
                  </div>

                  <div className="shrink-0 text-right">
                    <span className="text-[10px] text-gray-500 block uppercase font-mono mb-1">Status</span>
                    <span className={`px-3 py-1.5 rounded-lg text-xs font-bold font-mono ${
                      selectedCred.status === 'verified' ? 'bg-[#00E676]/10 text-[#00E676] border border-[#00E676]/20' :
                      selectedCred.status === 'failed' ? 'bg-[#F04040]/10 text-[#F04040] border border-[#F04040]/20' :
                      'bg-[#EFB01F]/10 text-[#EFB01F] border border-[#EFB01F]/20'
                    }`}>
                      {selectedCred.status.toUpperCase()}
                    </span>
                  </div>
                </div>

                {/* Visual Document Scan View */}
                <div className="border border-white/5 bg-[#0B121C] rounded-xl p-4 space-y-3 shadow-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider font-mono">Candidate Document Real-time Scan</span>
                    <span className="text-[9px] text-[#00BAC8] font-mono font-bold bg-[#00BAC8]/10 px-2 py-0.5 rounded border border-[#00BAC8]/20">11-PT AUDITED</span>
                  </div>
                  <div className="rounded-xl overflow-hidden shadow-2xl">
                    <ScannedDocumentViewer 
                      credentialName={selectedCred.name}
                      candidateName={candidate.name}
                      candidateRole={candidate.role}
                      serialId={selectedCred.id}
                      expiryDate={selectedCred.expiryDate}
                    />
                  </div>
                </div>

                {/* Dylan Vision Auditor Simulation */}
                <div className="border border-[#00BAC8]/20 bg-[#0B121C] rounded-xl p-5 space-y-4 shadow-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-[#00BAC8] animate-pulse" />
                      <span className="text-xs font-bold font-display text-[#00BAC8]">Dylan Vision Document Audit Engine</span>
                    </div>
                    <span className="text-[9px] text-[#00E676] font-mono font-bold bg-[#00E676]/10 px-2 py-0.5 rounded border border-[#00E676]/20">Active</span>
                  </div>

                  <p className="text-xs text-gray-400">
                    Dylan integrates with Gemini to extract text, check candidate identity alignment, and evaluate compliance. Upload a real PDF/Image or select a sample:
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {SAMPLE_FILES.map((file, idx) => (
                      <button
                        key={idx}
                        type="button"
                        disabled={auditing}
                        onClick={() => handleRunVisionAudit(file)}
                        className="p-2.5 text-left rounded-lg bg-[#04080E]/80 border border-white/5 hover:border-[#00BAC8]/40 hover:bg-[#04080E] text-xs font-mono text-gray-300 flex items-center justify-between group transition-colors disabled:opacity-50"
                      >
                        <div className="truncate pr-2">
                          <span className="text-gray-400 font-bold block truncate group-hover:text-white transition-colors">{file.name}</span>
                          <span className="text-[9px] text-gray-500 block">{file.size}</span>
                        </div>
                        <FileUp className="w-4 h-4 text-[#00BAC8] shrink-0" />
                      </button>
                    ))}
                  </div>

                  <div className="pt-2 border-t border-white/5">
                    <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-white/10 hover:border-[#00BAC8]/40 bg-[#04080E]/40 hover:bg-[#04080E]/60 rounded-xl cursor-pointer group transition-all text-center">
                      <Upload className="w-6 h-6 text-gray-500 group-hover:text-[#00BAC8] mb-1.5" />
                      <span className="text-xs font-medium text-gray-300 group-hover:text-white">Upload Real Document (PDF, JPEG, PNG)</span>
                      <span className="text-[9px] text-gray-500 mt-1 font-mono">Analyzed dynamically by live Gemini AI (No guessing)</span>
                      <input 
                        type="file" 
                        accept=".pdf,image/*" 
                        onChange={handleFileUpload} 
                        disabled={auditing}
                        className="hidden" 
                      />
                    </label>
                  </div>

                  {auditing && (
                    <div className="py-4 flex flex-col items-center justify-center text-center gap-2">
                      <div className="w-6 h-6 border-2 border-[#00BAC8] border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-[10px] text-gray-400 font-mono">Dylan is checking document validity and exipries via Gemini Vision API...</span>
                    </div>
                  )}

                  {visionReport && (
                    <div className="bg-[#04080E] border border-[#00BAC8]/20 rounded-lg p-3.5 text-[10px] text-[#00BAC8] font-mono leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
                      {visionReport}
                    </div>
                  )}
                </div>
              </div>

              {/* Action Workspace Panel */}
              <div className="bg-[#0B121C] border border-white/5 rounded-xl p-4 space-y-4 mt-6">
                <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block">Manual Override and Corrections</span>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="text-[9px] text-gray-500 font-mono block mb-1">Audit Document Expiry</label>
                    <input 
                      type="date"
                      value={manualExpiry}
                      onChange={(e) => setManualExpiry(e.target.value)}
                      className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                    />
                  </div>

                  <div>
                    <label className="text-[9px] text-gray-500 font-mono block mb-1">Compliance Notes</label>
                    <input 
                      type="text"
                      value={manualNote}
                      onChange={(e) => setManualNote(e.target.value)}
                      placeholder="e.g. Scanned copy verified manually"
                      className="w-full bg-[#04080E] border border-white/10 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#00BAC8] text-white"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-white/5">
                  <button
                    onClick={() => handleSaveCredential('failed')}
                    className="px-3.5 py-2 border border-[#F04040]/30 hover:bg-[#F04040]/10 text-[#F04040] text-xs font-bold rounded-lg transition-colors"
                  >
                    Mark Failed
                  </button>
                  <button
                    onClick={() => handleSaveCredential('verified')}
                    className="px-4 py-2 bg-[#00BAC8] text-[#04080E] text-xs font-bold rounded-lg hover:opacity-95 transition-colors"
                  >
                    Verify &amp; Approve
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center text-gray-500">
              <AlertCircle className="w-12 h-12 text-gray-700 mb-3" />
              <span className="text-xs">Select a credential item from the checklist to begin auditing.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
