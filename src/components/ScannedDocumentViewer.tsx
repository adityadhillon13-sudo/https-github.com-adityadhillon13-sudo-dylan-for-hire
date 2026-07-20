import React from 'react';
import { Shield, Check, Calendar, User, FileText, Activity, AlertCircle, Award, CreditCard, Heart } from 'lucide-react';

interface ScannedDocumentViewerProps {
  credentialName: string;
  candidateName: string;
  candidateRole: string;
  serialId: string;
  expiryDate?: string;
}

export default function ScannedDocumentViewer({
  credentialName,
  candidateName,
  candidateRole,
  serialId,
  expiryDate = '12/31/2027'
}: ScannedDocumentViewerProps) {
  const normName = credentialName.toLowerCase();

  // Helper to get formatted date from offset
  const getMockDate = (offsetDays: number) => {
    const d = new Date();
    d.setDate(d.getDate() - offsetDays);
    return d.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' });
  };

  // Render NYS Nursing License / Registry Card
  if (normName.includes('license') || normName.includes('registry') || normName.includes('licensure')) {
    return (
      <div className="border-4 border-double border-cyan-800 bg-[#FAF9F5] p-5 rounded-lg shadow-inner text-cyan-950 font-sans relative overflow-hidden h-[340px] flex flex-col justify-between">
        {/* Background watermarks */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.03] select-none rotate-12">
          <div className="text-8xl font-black">NYS EDUCATION</div>
        </div>

        {/* Header */}
        <div className="border-b border-cyan-800/40 pb-2 flex justify-between items-start">
          <div className="text-left">
            <h5 className="text-[10px] font-black tracking-widest text-cyan-800 uppercase">State Education Department</h5>
            <h4 className="text-sm font-black font-serif tracking-tight mt-0.5">THE UNIVERSITY OF THE STATE OF NEW YORK</h4>
            <p className="text-[9px] text-gray-500 italic">Office of the Professions - Nurse Registration Division</p>
          </div>
          <span className="text-[8px] bg-emerald-500/10 text-emerald-800 px-1.5 py-0.5 rounded border border-emerald-500/30 font-bold font-mono uppercase">
            ACTIVE REGISTRY
          </span>
        </div>

        {/* Card Body */}
        <div className="my-auto space-y-3">
          <div className="text-center">
            <p className="text-[8px] uppercase tracking-wider text-cyan-800 font-mono">This certifies that the candidate named below is licensed as a</p>
            <h3 className="text-lg font-black tracking-wide font-serif text-cyan-900 uppercase my-0.5">{candidateRole === 'RN' ? 'Registered Professional Nurse (RN)' : candidateRole === 'LPN' ? 'Licensed Practical Nurse (LPN)' : 'Certified Nursing Assistant (CNA)'}</h3>
          </div>

          <div className="grid grid-cols-2 gap-4 bg-cyan-900/5 p-3 rounded border border-cyan-800/10">
            <div>
              <span className="text-[7px] text-cyan-800/80 uppercase font-mono block">Licensee Name</span>
              <strong className="text-xs font-bold text-cyan-950 uppercase block font-serif">{candidateName}</strong>
            </div>
            <div>
              <span className="text-[7px] text-cyan-800/80 uppercase font-mono block">Registry License No.</span>
              <strong className="text-xs font-bold text-cyan-950 font-mono block tracking-widest">
                {candidateRole}-{serialId.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 7)}
              </strong>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-cyan-800/30 pt-2 flex justify-between items-end text-[8px] font-mono">
          <div>
            <p className="text-gray-500">AUTHORIZED REGISTRY KEY</p>
            <p className="font-bold text-cyan-900">NYS-DOH-{serialId.toUpperCase().slice(0, 10)}</p>
          </div>
          <div className="text-right">
            <p className="text-gray-500">REGISTRATION EXPIRES</p>
            <p className="font-bold text-amber-700">{expiryDate}</p>
          </div>
        </div>
      </div>
    );
  }

  // Render American Heart Association BLS Card
  if (normName.includes('bls') || normName.includes('cpr') || normName.includes('cardiopulmonary')) {
    return (
      <div className="border-t-[10px] border-t-red-600 border border-gray-300 bg-white p-5 rounded-lg shadow-inner text-gray-900 font-sans relative overflow-hidden h-[340px] flex flex-col justify-between">
        {/* AHA Heart Symbol representation in BG */}
        <div className="absolute right-4 bottom-4 pointer-events-none opacity-[0.04]">
          <Heart className="w-48 h-48 fill-red-600 text-red-600" />
        </div>

        {/* Header */}
        <div className="flex justify-between items-start border-b pb-2">
          <div className="flex items-center gap-1.5">
            <div className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center text-white font-black text-xs">A</div>
            <div>
              <h4 className="text-[10px] font-black text-red-600 tracking-wider">American Heart Association.</h4>
              <p className="text-[8px] text-gray-500 font-bold uppercase font-mono">Basic Life Support</p>
            </div>
          </div>
          <span className="text-[9px] bg-red-500 text-white px-2 py-0.5 rounded font-black font-mono uppercase tracking-widest text-[8px]">
            BLS PROVIDER
          </span>
        </div>

        {/* Content */}
        <div className="my-auto space-y-3">
          <div className="space-y-1">
            <span className="text-[7px] text-gray-400 uppercase font-mono block">This certifies that</span>
            <h3 className="text-sm font-black text-gray-800 uppercase font-serif tracking-tight">{candidateName}</h3>
            <p className="text-[8px] text-gray-500 leading-normal">
              has successfully completed the cognitive and skills evaluations in accordance with the curriculum of the American Heart Association Basic Life Support (CPR and AED) Program.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 bg-gray-50 p-2.5 rounded border border-gray-100">
            <div>
              <span className="text-[7px] text-gray-400 uppercase font-mono block">Issue Date</span>
              <strong className="text-xs font-bold text-gray-700 font-mono">{getMockDate(180)}</strong>
            </div>
            <div>
              <span className="text-[7px] text-gray-400 uppercase font-mono block">Recommended Renewal Date</span>
              <strong className="text-xs font-bold text-red-600 font-mono">{expiryDate}</strong>
            </div>
          </div>
        </div>

        {/* AHA Footer */}
        <div className="border-t pt-2 flex justify-between items-center text-[8px] font-mono text-gray-500">
          <div>
            <p>eCard Code: <strong className="text-gray-800">265501839842</strong></p>
            <p>Training Center ID: <strong className="text-gray-800">NY-983421 (Citadel-EMS)</strong></p>
          </div>
          <div className="text-right">
            <span className="inline-block px-1.5 py-0.5 border border-emerald-500/20 text-emerald-600 rounded bg-emerald-500/5 font-bold">
              VERIFIED AUTHENTIC
            </span>
          </div>
        </div>
      </div>
    );
  }

  // Render TB Test / PPD / QuantiFERON Clinical Lab Report
  if (normName.includes('ppd') || normName.includes('tb') || normName.includes('tuberculosis') || normName.includes('quantiferon')) {
    return (
      <div className="border border-gray-200 bg-white p-5 rounded-lg shadow-inner text-gray-900 font-mono relative overflow-hidden h-[340px] flex flex-col justify-between">
        {/* Lab Letterhead */}
        <div className="border-b-2 border-gray-800 pb-2">
          <div className="flex justify-between items-start">
            <div className="text-left font-sans">
              <h4 className="text-xs font-black tracking-tight text-slate-800">METRO DIAGNOSTIC CLINICAL LABS</h4>
              <p className="text-[7px] text-gray-400">100 Broadway, New York, NY 10005 · Tel: (212) 555-0199</p>
            </div>
            <div className="text-right text-[8px] text-gray-500">
              <p>REPORT DATE: {getMockDate(45)}</p>
              <p>LAB ACCREDITED: CLIA-99D02834</p>
            </div>
          </div>
        </div>

        {/* Patient Metadata */}
        <div className="grid grid-cols-2 gap-2 text-[8px] bg-slate-50 p-2 border border-slate-100 rounded my-1.5 font-sans">
          <div>
            <span className="text-gray-400 block">PATIENT:</span>
            <strong className="text-slate-800 uppercase">{candidateName}</strong>
          </div>
          <div>
            <span className="text-gray-400 block">REFERRED BY:</span>
            <strong className="text-slate-800">DYLAN AGENT RECRUITING</strong>
          </div>
        </div>

        {/* Lab Results Table */}
        <div className="flex-1 my-1.5 text-[8px] space-y-1">
          <div className="grid grid-cols-12 border-b border-gray-800 font-bold pb-1 text-gray-600 uppercase">
            <span className="col-span-5">Test Description</span>
            <span className="col-span-3 text-center">Result</span>
            <span className="col-span-2 text-center">Flag</span>
            <span className="col-span-2 text-right">Reference</span>
          </div>

          <div className="grid grid-cols-12 py-1 border-b border-gray-100 items-center">
            <span className="col-span-5 font-sans font-bold">QuantiFERON-TB Gold Plus</span>
            <span className="col-span-3 text-center text-emerald-600 font-bold bg-emerald-500/10 px-1 py-0.5 rounded">NEGATIVE</span>
            <span className="col-span-2 text-center text-gray-400">-</span>
            <span className="col-span-2 text-right text-gray-400">Negative</span>
          </div>

          <div className="grid grid-cols-12 py-1 text-gray-500">
            <span className="col-span-5">TB Antigen minus Nil</span>
            <span className="col-span-3 text-center">0.02 IU/mL</span>
            <span className="col-span-2 text-center">-</span>
            <span className="col-span-2 text-right">&lt; 0.35</span>
          </div>

          <div className="p-1.5 bg-[#00E676]/5 border border-[#00E676]/20 rounded text-[7px] text-emerald-800 leading-normal font-sans mt-2">
            <strong>Medical Assessment:</strong> No evidence of active or latent Mycobacterium tuberculosis infection. Candidate is clinically cleared.
          </div>
        </div>

        {/* Lab Signature */}
        <div className="border-t pt-1.5 flex justify-between items-end text-[7px] text-gray-500">
          <div>
            <p>Accession ID: <strong className="text-gray-800">MD-2026-{serialId.toUpperCase().slice(0, 5)}</strong></p>
            <p>Specimen Source: Blood Venipuncture</p>
          </div>
          <div className="text-right font-serif italic text-gray-800">
            <p className="border-b border-gray-400 pb-0.5">Dr. Kenneth Cole, MD</p>
            <p className="text-[6px] text-gray-400 not-italic font-mono uppercase">Laboratory Director</p>
          </div>
        </div>
      </div>
    );
  }

  // Render Annual Physical Examination Certificate
  if (normName.includes('physical') || normName.includes('exam') || normName.includes('assessment') || normName.includes('health')) {
    return (
      <div className="border border-slate-300 bg-[#FAF9F6] p-5 rounded-lg shadow-inner text-slate-800 font-sans relative overflow-hidden h-[340px] flex flex-col justify-between">
        {/* Clinic Header */}
        <div className="border-b border-slate-300 pb-2 text-center">
          <h4 className="text-xs font-black tracking-widest text-slate-700 uppercase">NYC Occupational Health &amp; Wellness</h4>
          <p className="text-[7px] text-gray-500">Approved NYS Department of Health Healthcare Screening Site</p>
        </div>

        {/* Form Body */}
        <div className="my-auto space-y-3 text-left">
          <div className="text-[10px] text-gray-500 uppercase tracking-widest font-mono text-center">Certificate of Medical Clearance</div>
          
          <p className="text-[10px] text-slate-700 leading-relaxed text-center italic px-3">
            "This is to certify that on <strong>{getMockDate(120)}</strong>, I performed a comprehensive physical examination on the healthcare practitioner named below."
          </p>

          <div className="bg-white border border-slate-200 p-2.5 rounded text-[9px] space-y-1">
            <div className="flex justify-between"><span className="text-gray-400 font-mono">Practitioner Name:</span> <strong className="text-slate-800 uppercase">{candidateName}</strong></div>
            <div className="flex justify-between"><span className="text-gray-400 font-mono">Height / Weight:</span> <strong className="text-slate-800">5' 6" / 142 lbs</strong></div>
            <div className="flex justify-between"><span className="text-gray-400 font-mono">Vital Signs:</span> <strong className="text-slate-800">BP: 118/76 | HR: 68 bpm</strong></div>
            <div className="flex justify-between"><span className="text-gray-400 font-mono">Habitus / Vision:</span> <strong className="text-slate-800">Normal / 20-20 Corrected</strong></div>
          </div>

          <div className="bg-emerald-500/5 border border-emerald-500/20 p-2 rounded text-[8px] text-emerald-800 font-mono leading-relaxed">
            <strong>✓ CLINICAL STATEMENT:</strong> Candidate is found to be in robust physical health, free from contagious diseases, and cleared to perform full duties as a <strong>{candidateRole}</strong> without physical or cognitive limitations.
          </div>
        </div>

        {/* Physical Footer */}
        <div className="border-t border-slate-200 pt-2 flex justify-between items-end text-[7px] font-mono text-gray-500">
          <div>
            <p>Verification Key: <strong className="text-gray-800">PHY-CLE-{serialId.toUpperCase().slice(0, 6)}</strong></p>
            <p>NYS Provider License: #029481</p>
          </div>
          <div className="text-right">
            <p className="font-serif italic text-slate-800 border-b border-gray-300 pb-0.5">Theresa Vance, NP</p>
            <p className="text-[6px] uppercase text-gray-400">Nurse Practitioner</p>
          </div>
        </div>
      </div>
    );
  }

  // Render Two Forms of ID (NY Driver's License & Passport mockup)
  if (normName.includes('id') || normName.includes('ssn') || normName.includes('passport') || normName.includes('identity')) {
    return (
      <div className="border border-slate-400 bg-slate-900 p-5 rounded-lg shadow-2xl text-white font-sans relative overflow-hidden h-[340px] flex flex-col justify-between">
        {/* Header split */}
        <div className="flex justify-between items-start border-b border-white/10 pb-1.5">
          <span className="text-[8px] text-gray-400 uppercase tracking-widest font-mono">Two Forms of Verified Identity</span>
          <span className="text-[8px] font-mono font-bold text-cyan-400">NYS-SECURE-ID</span>
        </div>

        {/* 2 ID cards rendered inside */}
        <div className="my-auto space-y-4">
          {/* NY Driver License mock card */}
          <div className="bg-gradient-to-r from-blue-900 to-sky-800 rounded-lg p-2.5 border border-white/10 text-white font-sans flex items-start gap-2.5 h-[105px] relative overflow-hidden">
            <div className="absolute right-2 top-2 opacity-5 pointer-events-none text-2xl font-black">NY</div>
            {/* Mock Portrait */}
            <div className="w-14 h-16 bg-white/10 border border-white/20 rounded flex items-center justify-center shrink-0">
              <User className="w-10 h-10 text-white/30" />
            </div>
            {/* Metadata */}
            <div className="text-[7px] space-y-0.5 flex-1 min-w-0 leading-tight">
              <p className="text-[8px] font-black text-amber-300">NEW YORK STATE DRIVER LICENSE</p>
              <p className="text-[9px] font-black tracking-wider text-white">ID: NY-889-12-{serialId.toUpperCase().slice(0, 4)}</p>
              <p><span className="text-white/60 uppercase">NAME:</span> <strong className="text-white uppercase">{candidateName}</strong></p>
              <p><span className="text-white/60">CLASS:</span> <strong>D</strong> · <span className="text-white/60">SEX:</span> <strong>F</strong></p>
              <p><span className="text-white/60">ADDRESS:</span> <span className="truncate">780 Grand Concourse, Bronx, NY 10451</span></p>
              <p className="text-amber-300 font-mono text-[6px] uppercase">State Holographic Authenticated</p>
            </div>
          </div>

          {/* Social Security / US Passport page mock */}
          <div className="bg-[#DFDCD4] rounded-lg p-2.5 border border-amber-950/10 text-amber-950 flex items-start gap-2.5 h-[105px] relative overflow-hidden">
            {/* Eagle Crest representation */}
            <div className="absolute right-3 top-3 opacity-10 pointer-events-none">
              <Award className="w-16 h-16 text-amber-900" />
            </div>
            {/* Mock Passport Portrait */}
            <div className="w-14 h-16 bg-amber-900/10 border border-amber-950/20 rounded flex items-center justify-center shrink-0">
              <User className="w-10 h-10 text-amber-950/25" />
            </div>
            {/* Metadata */}
            <div className="text-[7px] space-y-0.5 flex-1 min-w-0 leading-tight">
              <p className="text-[8px] font-black text-amber-900 uppercase tracking-tight">United States of America Passport</p>
              <p className="text-[9px] font-bold tracking-widest text-amber-950">No. 99824{serialId.toUpperCase().slice(0, 3)}</p>
              <p><span className="text-amber-950/60 uppercase">SURNAME:</span> <strong className="uppercase">{candidateName.split(' ')[1] || 'CANDIDATE'}</strong></p>
              <p><span className="text-amber-950/60 uppercase">GIVEN NAMES:</span> <strong className="uppercase">{candidateName.split(' ')[0] || 'NURSE'}</strong></p>
              <p><span className="text-amber-950/60">AUTHORITY:</span> <strong>DEPARTMENT OF STATE</strong></p>
              <p className="text-amber-800 font-serif font-bold italic text-[6px]">United States Federal Identification Verified</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-white/10 pt-1.5 flex justify-between items-center text-[7px] text-gray-500 font-mono">
          <span>OCR Identity Checksum</span>
          <span className="text-emerald-400 font-bold">100% ID MATCHED</span>
        </div>
      </div>
    );
  }

  // Render MMR Titers / Varicella Titers Lab Report
  if (normName.includes('mmr') || normName.includes('titer') || normName.includes('varicella') || normName.includes('measles') || normName.includes('titers')) {
    return (
      <div className="border border-slate-300 bg-white p-5 rounded-lg shadow-inner text-slate-800 font-mono relative overflow-hidden h-[340px] flex flex-col justify-between">
        {/* Lab Header */}
        <div className="border-b-2 border-slate-800 pb-1.5">
          <div className="flex justify-between items-center">
            <div className="font-sans">
              <h4 className="text-xs font-black text-slate-800 tracking-tight">BIO-LAB IMMUNOLOGY SERVICES</h4>
              <p className="text-[6px] text-gray-400">NYS Lic #LAB-00892 | CLIA Certified</p>
            </div>
            <div className="text-right text-[7px] text-gray-500">
              <p>REQ NO: MMR-9018</p>
              <p>DATE: {getMockDate(90)}</p>
            </div>
          </div>
        </div>

        {/* Patient Block */}
        <div className="bg-slate-50 border border-slate-100 p-1.5 rounded my-1 text-[7px] font-sans flex justify-between items-center">
          <div>PATIENT: <strong className="text-slate-800 uppercase">{candidateName}</strong></div>
          <div>ROLE: <strong>{candidateRole}</strong></div>
        </div>

        {/* Immunology results Table */}
        <div className="flex-1 my-1 text-[8px] space-y-1">
          <div className="grid grid-cols-12 border-b border-gray-400 font-bold text-gray-500 pb-0.5 uppercase">
            <span className="col-span-5">ANTIGEN PANEL</span>
            <span className="col-span-3 text-center">INDEX</span>
            <span className="col-span-4 text-right">STATUS</span>
          </div>

          <div className="grid grid-cols-12 py-0.5 border-b border-slate-100 items-center">
            <span className="col-span-5 font-sans font-bold">Rubeola (Measles) IgG</span>
            <span className="col-span-3 text-center">3.12 Ratio</span>
            <span className="col-span-4 text-right text-emerald-600 font-bold">POSITIVE (IMMUNE)</span>
          </div>

          <div className="grid grid-cols-12 py-0.5 border-b border-slate-100 items-center">
            <span className="col-span-5 font-sans font-bold">Mumps Virus IgG</span>
            <span className="col-span-3 text-center">2.88 Ratio</span>
            <span className="col-span-4 text-right text-emerald-600 font-bold">POSITIVE (IMMUNE)</span>
          </div>

          <div className="grid grid-cols-12 py-0.5 border-b border-slate-100 items-center">
            <span className="col-span-5 font-sans font-bold">Rubella Antibody IgG</span>
            <span className="col-span-3 text-center">31.4 IU/mL</span>
            <span className="col-span-4 text-right text-emerald-600 font-bold">POSITIVE (IMMUNE)</span>
          </div>

          <div className="grid grid-cols-12 py-0.5 items-center">
            <span className="col-span-5 font-sans font-bold">Varicella Zoster IgG</span>
            <span className="col-span-3 text-center">450 mIU/mL</span>
            <span className="col-span-4 text-right text-emerald-600 font-bold">POSITIVE (IMMUNE)</span>
          </div>

          <div className="p-1 bg-[#00E676]/5 border border-[#00E676]/20 rounded text-[7px] text-emerald-800 font-sans leading-normal mt-1.5">
            <strong>LAB COMMENTARY:</strong> All titer indices exceed the protective threshold limit. High level antibodies confirmed. Safe for patient contact.
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 pt-1 flex justify-between items-center text-[7px] text-gray-500">
          <span>Batch No: IMM-2026-90184</span>
          <span>Verified: <strong>NYS Titer Ledger</strong></span>
        </div>
      </div>
    );
  }

  // Render Liability / Malpractice Insurance
  if (normName.includes('insurance') || normName.includes('liability') || normName.includes('malpractice') || normName.includes('coverage')) {
    return (
      <div className="border border-slate-300 bg-white p-5 rounded-lg shadow-inner text-slate-800 font-sans relative overflow-hidden h-[340px] flex flex-col justify-between">
        {/* Insurance Header */}
        <div className="border-b-2 border-slate-800 pb-1.5 flex justify-between items-start">
          <div>
            <h4 className="text-[10px] font-black text-slate-900 tracking-tight">CERTIFICATE OF LIABILITY INSURANCE</h4>
            <p className="text-[7px] text-gray-400 font-mono">ACORD FORM LAYOUT (MODIFIED NY-SPEC)</p>
          </div>
          <span className="text-[7px] border border-[#00E676]/20 bg-emerald-500/5 text-emerald-600 px-1 rounded font-bold font-mono">ACTIVE POLICY</span>
        </div>

        {/* Insurance Details */}
        <div className="my-auto space-y-2 text-left text-[8px]">
          <div className="grid grid-cols-2 gap-3">
            <div className="border border-slate-150 p-2 rounded bg-slate-50 space-y-0.5">
              <span className="text-gray-400 uppercase font-mono block">PRODUCER / AGENCY</span>
              <strong className="text-slate-700 block uppercase">NURSES DIRECT INSURANCE BROKERS</strong>
              <p className="text-gray-400">120 Pine St, New York, NY 10005</p>
            </div>
            <div className="border border-slate-150 p-2 rounded bg-slate-50 space-y-0.5">
              <span className="text-gray-400 uppercase font-mono block">INSURED / CANDIDATE</span>
              <strong className="text-slate-800 block uppercase">{candidateName}</strong>
              <p className="text-gray-500">Role: Registered Professional Nurse ({candidateRole})</p>
            </div>
          </div>

          <div className="border border-slate-150 rounded overflow-hidden">
            <div className="grid grid-cols-12 bg-slate-100 font-bold border-b p-1 text-gray-600">
              <span className="col-span-5">TYPE OF INSURANCE</span>
              <span className="col-span-4">POLICY NUMBER</span>
              <span className="col-span-3 text-right">LIMITS</span>
            </div>
            <div className="grid grid-cols-12 p-1.5 items-center">
              <span className="col-span-5 font-bold text-slate-800">Professional Medical Liability (Nursing)</span>
              <span className="col-span-4 font-mono">NY-PL-{serialId.toUpperCase().slice(0, 6)}</span>
              <div className="col-span-3 text-right font-mono space-y-0.5">
                <p>Occur: $1,000,000</p>
                <p>Aggre: $3,000,000</p>
              </div>
            </div>
          </div>

          <div className="bg-emerald-500/5 border border-emerald-500/10 p-1.5 rounded text-[7px] text-emerald-800 font-mono">
            <strong>POLICY STATUS:</strong> Active, paid in full. No claims listed or pending. Expiration matches {expiryDate}.
          </div>
        </div>

        {/* Footer */}
        <div className="border-t pt-1.5 flex justify-between items-center text-[7px] text-gray-400 font-mono">
          <span>AUTHORIZED BROKER ID: #90124</span>
          <span>Verified on ACORD registry</span>
        </div>
      </div>
    );
  }

  // Default: Render Candidate Professional Resume Document
  return (
    <div className="border border-gray-300 bg-white p-5 rounded-lg shadow-inner text-gray-800 font-sans relative overflow-hidden h-[340px] flex flex-col justify-between">
      {/* Header Resume */}
      <div className="border-b pb-2 flex justify-between items-end">
        <div className="text-left">
          <h3 className="text-sm font-black tracking-tight text-gray-900 uppercase font-serif">{candidateName}</h3>
          <p className="text-[9px] text-[#00BAC8] font-bold tracking-wider font-mono uppercase">{candidateRole} Practitioner · Borough: Queens, NYC</p>
        </div>
        <span className="text-[8px] text-gray-400 font-mono">OCR ANALYZED RESUME</span>
      </div>

      {/* Resume Body */}
      <div className="my-auto text-left space-y-2.5 text-[8px] leading-relaxed">
        <div>
          <h5 className="font-bold uppercase text-gray-500 tracking-wider font-mono text-[7px] border-b pb-0.5">Professional Summary</h5>
          <p className="text-gray-600 mt-0.5 italic">
            Highly experienced {candidateRole} with over 5 years of acute and long-term care experience in diverse hospital and clinical rehabilitation settings in the New York metropolitan area. Specialized in IV therapy, wound care, and EHR management.
          </p>
        </div>

        <div>
          <h5 className="font-bold uppercase text-gray-500 tracking-wider font-mono text-[7px] border-b pb-0.5">Clinical Work Experience</h5>
          <div className="space-y-1 mt-1">
            <p className="font-bold flex justify-between">
              <span>Citadel Rehabilitation Care Center (NYC)</span>
              <span className="text-gray-400 font-mono">03/2023 - Present</span>
            </p>
            <p className="text-gray-500 italic pl-1">Primary Charge Nurse - Geriatric Rehab Unit</p>
            
            <p className="font-bold flex justify-between">
              <span>Queens General Hospital</span>
              <span className="text-gray-400 font-mono">08/2021 - 02/2023</span>
            </p>
            <p className="text-gray-500 italic pl-1">Clinical Staff Nurse ({candidateRole}) - Medical-Surgical Unit</p>
          </div>
        </div>

        <div>
          <h5 className="font-bold uppercase text-gray-500 tracking-wider font-mono text-[7px] border-b pb-0.5">Education &amp; Core Certifications</h5>
          <p className="text-gray-600 mt-0.5 font-semibold">
            Associate of Applied Science in Nursing (AAS) · NYS Licensed Registered Professional Nurse · AHA BLS/ACLS Certified
          </p>
        </div>
      </div>

      {/* Resume Footer */}
      <div className="border-t pt-1.5 flex justify-between items-center text-[7px] text-gray-400 font-mono">
        <span>Verified Identity Ref: {serialId}</span>
        <span className="text-emerald-500 font-bold">Resume Complete</span>
      </div>
    </div>
  );
}
