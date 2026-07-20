export type CandidateRole = 'CNA' | 'LPN' | 'RN';

export interface CredentialStatus {
  id: string;
  name: string;
  required: boolean;
  status: 'pending' | 'verified' | 'failed';
  expiryDate?: string;
  notes?: string;
}

export interface Candidate {
  id: string;
  name: string;
  phone: string;
  email: string;
  role: CandidateRole;
  borough: 'Bronx' | 'Brooklyn' | 'Manhattan' | 'Queens' | 'Staten Island';
  status: 'Intake' | 'Captured' | 'Audited' | 'Shift Matched' | 'Placed';
  appliedDate: string;
  lastContactDate: string;
  credentials: CredentialStatus[];
  optedOut: boolean;
  score?: number; // Matching score
}

export interface Shift {
  id: string;
  facility: string;
  role: CandidateRole;
  borough: 'Bronx' | 'Brooklyn' | 'Manhattan' | 'Queens' | 'Staten Island';
  timeSlot: 'AM' | 'PM' | 'Overnight';
  hourlyRate: number;
  status: 'Open' | 'Matched' | 'Closed';
  matchedCandidateId?: string;
  date: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'success';
  service: 'orchestrator' | 'gmail_listener' | 'sms_poll' | 'gemini_vision';
  message: string;
}

export interface ReviewItem {
  id: string;
  candidateId: string;
  candidateName: string;
  channel: 'SMS' | 'Email';
  receivedMessage: string;
  suggestedReply: string;
  status: 'Pending' | 'Approved' | 'Sent' | 'Rejected';
  timestamp: string;
}

export interface SystemSettings {
  agencyName: string;
  supportPhone: string;
  supportEmail: string;
  optOutKeywords: string[];
  autoMatchThreshold: number;
  openPhoneLine: string;
}
