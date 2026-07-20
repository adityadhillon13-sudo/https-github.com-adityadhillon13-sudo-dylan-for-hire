import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";
import { Candidate, Shift, LogEntry, ReviewItem, SystemSettings, CredentialStatus } from "./src/types";

const app = express();
app.use(express.json());

const PORT = 3000;

// Lazy-loaded Gemini AI client helper to avoid startup crash if key is missing
let aiClient: GoogleGenAI | null = null;
function getGeminiClient(): GoogleGenAI | null {
  if (!aiClient) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (apiKey) {
      try {
        aiClient = new GoogleGenAI({
          apiKey: apiKey,
          httpOptions: {
            headers: {
              'User-Agent': 'aistudio-build',
            }
          }
        });
      } catch (err) {
        console.error("Failed to initialize Gemini Client:", err);
      }
    }
  }
  return aiClient;
}

// ==========================================
// MOCK DATA STORE (BlueLine NYC Context)
// ==========================================

let systemSettings: SystemSettings = {
  agencyName: "BlueLine Staffing NYC",
  supportPhone: "551-250-6678",
  supportEmail: "intake@bluelinestaffing.com",
  optOutKeywords: ["STOP", "UNSUBSCRIBE", "QUIT", "CANCEL", "OPT OUT"],
  autoMatchThreshold: 0.8,
  openPhoneLine: "+15512506678"
};

// Permanent opt-out registry
let permanentOptOuts: string[] = ["+15550198811", "+15550293344"];

// Initial logs
let logs: LogEntry[] = [
  {
    id: "l1",
    timestamp: new Date(Date.now() - 3600000 * 2).toISOString(),
    level: "success",
    service: "orchestrator",
    message: "Dylan Back Office Initialization complete."
  },
  {
    id: "l2",
    timestamp: new Date(Date.now() - 3600000 * 1.8).toISOString(),
    level: "info",
    service: "gmail_listener",
    message: "Gmail Pub/Sub 24/7 listener started. Watching inbox for candidate applications."
  },
  {
    id: "l3",
    timestamp: new Date(Date.now() - 3600000 * 1.5).toISOString(),
    level: "info",
    service: "sms_poll",
    message: "SMS OpenPhone 24/7 polling service connected. Fetching messages every 60s."
  }
];

const createInitialCredentials = (role: string): CredentialStatus[] => {
  const isCNA = role === 'CNA';
  const req = (name: string, required = true): CredentialStatus => ({
    id: name.toLowerCase().replace(/[^a-z0-9]/g, "_"),
    name,
    required,
    status: Math.random() > 0.45 ? 'verified' : (Math.random() > 0.5 ? 'pending' : 'failed'),
    expiryDate: Math.random() > 0.2 ? new Date(Date.now() + 3600000 * 24 * Math.floor(Math.random() * 300 + 30)).toISOString().split('T')[0] : undefined,
    notes: Math.random() > 0.8 ? "Verified via New York Registry." : undefined
  });

  return [
    req("NYS Nurse License / Registry ID"),
    req("BLS Certification (CPR)"),
    req("TB Test Result (PPD / QuantiFERON)"),
    req("MMR Immunization (Measles, Mumps, Rubella)"),
    req("Annual Physical Exam"),
    req("Resume / CV"),
    req("I-9 Employment Authorization"),
    req("W-4 Tax Form"),
    // Optional / Recommended credentials (Round 4 / 11-point total split)
    req("Hepatitis B Vaccination / Declination", false),
    req("Annual Flu Vaccine / Declination", false),
    // Extra credential specific to high-level RN/LPN or applications
    req("Employment Application Form", false)
  ];
};

// 37 active candidates (representing BlueLine NY actual counts: 22 CNA, 9 LPN, 6 RN)
let candidates: Candidate[] = [];

// Prepopulate 22 CNAs
const cnaNames = [
  "Amara Okafor", "Brianna Davis", "Carlos Mendez", "Devon Harris", "Lorna Brown", 
  "Fatima Diop", "Grace Kim", "Hassan Mahmoud", "Irene Adler", "Jamal Crawford",
  "Khadija Begum", "Luis Rodriguez", "Mei Chen", "Nia Tolliver", "Oscar Peterson",
  "Priya Patel", "Quincy Adams", "Rosa Delgado", "Samuel Green", "Tariq Ali",
  "Ulysses Grant", "Valerie Jenkins"
];
cnaNames.forEach((name, i) => {
  const statusPool: Candidate['status'][] = ['Placed', 'Shift Matched', 'Audited', 'Captured', 'Intake'];
  const status = statusPool[i % statusPool.length];
  const boroughPool: Candidate['borough'][] = ['Brooklyn', 'Bronx', 'Manhattan', 'Queens', 'Staten Island'];
  const borough = boroughPool[i % boroughPool.length];
  
  candidates.push({
    id: `cand-cna-${i + 1}`,
    name,
    phone: `+15550100${10 + i}`,
    email: `${name.toLowerCase().replace(/\s/g, '.')}@example.com`,
    role: "CNA",
    borough,
    status,
    appliedDate: new Date(Date.now() - 3600000 * 24 * (5 + i)).toISOString(),
    lastContactDate: new Date(Date.now() - 3600000 * (i + 1)).toISOString(),
    credentials: createInitialCredentials("CNA"),
    optedOut: false
  });
});

// Prepopulate 9 LPNs
const lpnNames = [
  "Agnes O'Connor", "Benjamin Miller", "Rose Martine Saintil", "David Tennant", "Emily Blunt",
  "Fiona Gallagher", "George Costanza", "Hannah Abbott", "Ian McKellen"
];
lpnNames.forEach((name, i) => {
  const statusPool: Candidate['status'][] = ['Placed', 'Shift Matched', 'Audited', 'Captured'];
  const status = statusPool[i % statusPool.length];
  const boroughPool: Candidate['borough'][] = ['Brooklyn', 'Queens', 'Manhattan', 'Bronx'];
  const borough = boroughPool[i % boroughPool.length];

  candidates.push({
    id: `cand-lpn-${i + 1}`,
    name,
    phone: `+15550200${10 + i}`,
    email: `${name.toLowerCase().replace(/\s/g, '.')}@example.com`,
    role: "LPN",
    borough,
    status,
    appliedDate: new Date(Date.now() - 3600000 * 24 * (3 + i)).toISOString(),
    lastContactDate: new Date(Date.now() - 3600000 * (i * 2 + 3)).toISOString(),
    credentials: createInitialCredentials("LPN"),
    optedOut: false
  });
});

// Prepopulate 6 RNs
const rnNames = [
  "Alice Sterling", "Bruce Wayne", "Clark Kent", "Diana Prince", "Ethan Hunt", "Frank Castle"
];
rnNames.forEach((name, i) => {
  const statusPool: Candidate['status'][] = ['Placed', 'Shift Matched', 'Audited'];
  const status = statusPool[i % statusPool.length];
  const boroughPool: Candidate['borough'][] = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx'];
  const borough = boroughPool[i % boroughPool.length];

  candidates.push({
    id: `cand-rn-${i + 1}`,
    name,
    phone: `+15550300${10 + i}`,
    email: `${name.toLowerCase().replace(/\s/g, '.')}@example.com`,
    role: "RN",
    borough,
    status,
    appliedDate: new Date(Date.now() - 3600000 * 24 * (1 + i)).toISOString(),
    lastContactDate: new Date(Date.now() - 3600000 * (i * 3 + 2)).toISOString(),
    credentials: createInitialCredentials("RN"),
    optedOut: false
  });
});

// Mock shifts
let shifts: Shift[] = [
  {
    id: "shift-1",
    facility: "Brooklyn Heights Care Center",
    role: "CNA",
    borough: "Brooklyn",
    timeSlot: "AM",
    hourlyRate: 35,
    status: "Open",
    date: new Date(Date.now() + 3600000 * 24 * 2).toISOString().split('T')[0]
  },
  {
    id: "shift-2",
    facility: "Bronx Rehabilitation Hospital",
    role: "RN",
    borough: "Bronx",
    timeSlot: "PM",
    hourlyRate: 75,
    status: "Matched",
    matchedCandidateId: "cand-rn-1",
    date: new Date(Date.now() + 3600000 * 24 * 3).toISOString().split('T')[0]
  },
  {
    id: "shift-3",
    facility: "Queens Nursing Home",
    role: "LPN",
    borough: "Queens",
    timeSlot: "Overnight",
    hourlyRate: 50,
    status: "Open",
    date: new Date(Date.now() + 3600000 * 24 * 1).toISOString().split('T')[0]
  },
  {
    id: "shift-4",
    facility: "Allendale Rehabilitation NJ",
    role: "CNA",
    borough: "Manhattan",
    timeSlot: "PM",
    hourlyRate: 38,
    status: "Open",
    date: new Date(Date.now() + 3600000 * 24 * 4).toISOString().split('T')[0]
  },
  {
    id: "shift-5",
    facility: "Staten Island Senior Living",
    role: "CNA",
    borough: "Staten Island",
    timeSlot: "AM",
    hourlyRate: 34,
    status: "Open",
    date: new Date(Date.now() + 3600000 * 24 * 2).toISOString().split('T')[0]
  }
];

// Human in the Loop Review Queue
let reviewQueue: ReviewItem[] = [
  {
    id: "rev-1",
    candidateId: "cand-cna-5",
    candidateName: "Lorna Brown",
    channel: "SMS",
    receivedMessage: "Ok thank you. I am ready to start my shifts in July at Park Nursing home.",
    suggestedReply: "Hi Lorna, thanks for your reply! Dylan has locked in your interest for the July shifts at Park Nursing home. Please make sure your annual physical and MMR titers are uploaded so we can authorize this schedule.",
    status: "Pending",
    timestamp: new Date(Date.now() - 15 * 60000).toISOString()
  },
  {
    id: "rev-2",
    candidateId: "cand-lpn-3",
    candidateName: "Rose Martine Saintil",
    channel: "Email",
    receivedMessage: "Hi Mr Dylan, I have sent the requested documents by email. Please confirm that you have received them.",
    suggestedReply: "Hi Rose, thanks for confirming! I see your Registered Nurse medical credentials in our inbox. I am initiating the 11-point vision compliance audit now and will follow up with the facility details within 4 minutes. Have a great day!",
    status: "Pending",
    timestamp: new Date(Date.now() - 40 * 60000).toISOString()
  }
];


// ==========================================
// REST API ENDPOINTS
// ==========================================

// Settings
app.get("/api/settings", (req, res) => {
  res.json(systemSettings);
});

app.post("/api/settings", (req, res) => {
  systemSettings = { ...systemSettings, ...req.body };
  res.json(systemSettings);
});

// Opt-Outs
app.get("/api/optouts", (req, res) => {
  res.json(permanentOptOuts);
});

app.post("/api/optouts", (req, res) => {
  const { phone } = req.body;
  if (phone && !permanentOptOuts.includes(phone)) {
    permanentOptOuts.push(phone);
    // Find candidate and mark opted-out
    const candidate = candidates.find(c => c.phone === phone);
    if (candidate) {
      candidate.optedOut = true;
      candidate.status = "Intake"; // Reset or freeze
    }
    
    logs.push({
      id: `l-opt-${Date.now()}`,
      timestamp: new Date().toISOString(),
      level: "warn",
      service: "sms_poll",
      message: `Ironclad Opt-Out Sync: Added ${phone} to blacklist.`
    });
  }
  res.json(permanentOptOuts);
});

// Candidates
app.get("/api/candidates", (req, res) => {
  res.json(candidates);
});

app.post("/api/candidates", (req, res) => {
  const { name, phone, email, role, borough } = req.body;
  if (!name || !phone || !email || !role || !borough) {
    return res.status(400).json({ error: "Missing required candidate fields." });
  }

  const isBlacklisted = permanentOptOuts.includes(phone);

  const newCandidate: Candidate = {
    id: `cand-user-${Date.now()}`,
    name,
    phone,
    email,
    role,
    borough,
    status: isBlacklisted ? "Intake" : "Captured",
    appliedDate: new Date().toISOString(),
    lastContactDate: new Date().toISOString(),
    credentials: createInitialCredentials(role),
    optedOut: isBlacklisted
  };

  candidates.push(newCandidate);

  logs.push({
    id: `l-cand-${Date.now()}`,
    timestamp: new Date().toISOString(),
    level: isBlacklisted ? "warn" : "success",
    service: "gmail_listener",
    message: isBlacklisted 
      ? `Captured candidate ${name} (${role}) via application email, but phone is in permanent opt-out blacklist!`
      : `New candidate ${name} (${role}) captured and integrated into intake pipeline.`
  });

  res.status(201).json(newCandidate);
});

app.put("/api/candidates/:id", (req, res) => {
  const idx = candidates.findIndex(c => c.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: "Candidate not found" });

  candidates[idx] = { ...candidates[idx], ...req.body };
  res.json(candidates[idx]);
});

app.delete("/api/candidates/:id", (req, res) => {
  const candidate = candidates.find(c => c.id === req.params.id);
  if (candidate) {
    candidate.optedOut = true;
    if (!permanentOptOuts.includes(candidate.phone)) {
      permanentOptOuts.push(candidate.phone);
    }
    logs.push({
      id: `l-del-${Date.now()}`,
      timestamp: new Date().toISOString(),
      level: "warn",
      service: "orchestrator",
      message: `Candidate ${candidate.name} manually opted out and blacklisted.`
    });
  }
  res.json({ success: true });
});

// Shifts
app.get("/api/shifts", (req, res) => {
  res.json(shifts);
});

app.post("/api/shifts", (req, res) => {
  const { facility, role, borough, timeSlot, hourlyRate } = req.body;
  const newShift: Shift = {
    id: `shift-${Date.now()}`,
    facility,
    role,
    borough,
    timeSlot,
    hourlyRate: Number(hourlyRate),
    status: "Open",
    date: new Date(Date.now() + 3600000 * 24 * 3).toISOString().split('T')[0]
  };
  shifts.push(newShift);
  res.status(201).json(newShift);
});

app.post("/api/shifts/:id/match", (req, res) => {
  const { candidateId } = req.body;
  const shiftIdx = shifts.findIndex(s => s.id === req.params.id);
  if (shiftIdx === -1) return res.status(404).json({ error: "Shift not found" });

  const candidate = candidates.find(c => c.id === candidateId);
  if (!candidate) return res.status(404).json({ error: "Candidate not found" });

  shifts[shiftIdx].status = "Matched";
  shifts[shiftIdx].matchedCandidateId = candidateId;

  candidate.status = "Shift Matched";
  candidate.lastContactDate = new Date().toISOString();

  logs.push({
    id: `l-match-${Date.now()}`,
    timestamp: new Date().toISOString(),
    level: "success",
    service: "orchestrator",
    message: `Matched ${candidate.name} (${candidate.role}) to shift at ${shifts[shiftIdx].facility} (${shifts[shiftIdx].borough}). Notification dispatched.`
  });

  res.json(shifts[shiftIdx]);
});

// Review Queue
app.get("/api/review-queue", (req, res) => {
  res.json(reviewQueue.filter(item => item.status === "Pending"));
});

app.post("/api/review-queue/:id/approve", (req, res) => {
  const { updatedReply } = req.body;
  const item = reviewQueue.find(r => r.id === req.params.id);
  if (!item) return res.status(404).json({ error: "Review item not found" });

  item.status = "Approved";
  item.suggestedReply = updatedReply || item.suggestedReply;

  // Simulate sending
  setTimeout(() => {
    item.status = "Sent";
  }, 1000);

  // If this reply was an opt-out confirmation, sync the blacklist
  if (item.suggestedReply.toLowerCase().includes("marked your contact number as opted-out") || item.receivedMessage.toLowerCase().includes("stop")) {
    const candidate = candidates.find(c => c.id === item.candidateId);
    if (candidate && !permanentOptOuts.includes(candidate.phone)) {
      permanentOptOuts.push(candidate.phone);
      candidate.optedOut = true;
    }
  }

  // Update candidate's last contact
  const candidate = candidates.find(c => c.id === item.candidateId);
  if (candidate) {
    candidate.lastContactDate = new Date().toISOString();
  }

  logs.push({
    id: `l-approve-${Date.now()}`,
    timestamp: new Date().toISOString(),
    level: "success",
    service: item.channel === "SMS" ? "sms_poll" : "gmail_listener",
    message: `Human-approved reply sent to ${item.candidateName}: "${item.suggestedReply.substring(0, 45)}..."`
  });

  res.json({ success: true, item });
});

app.post("/api/review-queue/:id/reject", (req, res) => {
  const item = reviewQueue.find(r => r.id === req.params.id);
  if (!item) return res.status(404).json({ error: "Review item not found" });

  item.status = "Rejected";

  logs.push({
    id: `l-reject-${Date.now()}`,
    timestamp: new Date().toISOString(),
    level: "warn",
    service: item.channel === "SMS" ? "sms_poll" : "gmail_listener",
    message: `Operator rejected drafted response for ${item.candidateName}.`
  });

  res.json({ success: true, item });
});

// Logs
app.get("/api/logs", (req, res) => {
  res.json(logs);
});

app.post("/api/logs/clear", (req, res) => {
  logs = [
    {
      id: `l-${Date.now()}`,
      timestamp: new Date().toISOString(),
      level: "info",
      service: "orchestrator",
      message: "Console cleared by administrator."
    }
  ];
  res.json(logs);
});

// ==========================================
// SYSTEM OPERATIONS & SIMULATION RUNNERS
// ==========================================

// Run Daily Orchestrator Cron (Intake, Credential Audits, Shift Matching, Alert Reblasts)
app.post("/api/actions/run-daily-cron", (req, res) => {
  const sessionLogs: string[] = [];
  const logAndPush = (level: LogEntry['level'], message: string) => {
    const ts = new Date().toISOString();
    logs.push({
      id: `l-cron-${Date.now()}-${Math.random()}`,
      timestamp: ts,
      level,
      service: "orchestrator",
      message
    });
    sessionLogs.push(`[${ts.substring(11, 19)}] [${level.toUpperCase()}] ${message}`);
  };

  logAndPush("info", "Starting Daily Recruiting Orchestration Cycle (Cron Job)...");
  
  // Step 1: Capture & Dedup
  const uncaptured = candidates.filter(c => c.status === "Intake" && !c.optedOut);
  logAndPush("info", `STEP 1: Checking for new candidate registrations... Found ${uncaptured.length} uncaptured candidates.`);
  
  uncaptured.forEach(c => {
    c.status = "Captured";
    logAndPush("success", `STEP 1 SUCCESS: Ingested & parsed credentials checklist for ${c.name} (${c.role})`);
  });

  // Step 2: 11-point Credential Auditing via Vision Analyzer
  const captured = candidates.filter(c => c.status === "Captured" && !c.optedOut);
  logAndPush("info", `STEP 2: Launching Dylan Credential Audit Engine... Processing ${captured.length} profiles.`);
  
  captured.forEach(c => {
    // Randomly pass or fail some credentials to mimic real visual file checks
    let verifiedCount = 0;
    c.credentials.forEach(cred => {
      if (Math.random() > 0.2) {
        cred.status = "verified";
        verifiedCount++;
      } else {
        cred.status = "failed";
        cred.notes = "Illegible scan or expired. Human attention requested.";
      }
    });

    if (verifiedCount >= 9) {
      c.status = "Audited";
      logAndPush("success", `STEP 2 SUCCESS: Dylan AI Vision verified 11-point credentials for ${c.name} (${verifiedCount}/11 passed).`);
    } else {
      logAndPush("warn", `STEP 2 PENDING: ${c.name} holds missing or expired credentials. Alerts dispatched to submit outstanding documents.`);
    }
  });

  // Step 3: Shift Matching Matrix
  const audited = candidates.filter(c => c.status === "Audited" && !c.optedOut);
  const openShifts = shifts.filter(s => s.status === "Open");
  logAndPush("info", `STEP 3: Running Shift Matching Logic. Mapping ${audited.length} audited nurses against ${openShifts.length} open NYC slots.`);

  let matchCount = 0;
  openShifts.forEach(shift => {
    const perfectMatch = audited.find(cand => cand.role === shift.role && cand.borough === shift.borough);
    if (perfectMatch) {
      shift.status = "Matched";
      shift.matchedCandidateId = perfectMatch.id;
      perfectMatch.status = "Shift Matched";
      matchCount++;
      logAndPush("success", `STEP 3 MATCH: Paired ${perfectMatch.name} (${perfectMatch.role}) with ${shift.facility} in ${shift.borough} ($${shift.hourlyRate}/hr).`);
    }
  });
  logAndPush("info", `STEP 3 COMPLETE: Auto-matched ${matchCount} nurses to open facility schedules.`);

  // Step 4: Facility Alert Reblasts
  logAndPush("info", "STEP 4: Dispatching placement confirmations and alert reblasts to facilities...");
  logAndPush("success", `Daily Recruiting Cycle completed successfully. Total processed: ${candidates.length} nurses, Placements: ${shifts.filter(s => s.status === "Matched").length}`);

  res.json({ success: true, logs: sessionLogs });
});

// Simulate Inbound message (SMS or Email)
app.post("/api/actions/simulate-inbound", (req, res) => {
  const { candidateId, channel, messageText } = req.body;
  const candidate = candidates.find(c => c.id === candidateId);
  if (!candidate) return res.status(404).json({ error: "Candidate not found" });

  const lowText = messageText.toLowerCase();
  let suggestedReply = "";
  let needsHuman = true;

  // Process rules following 07_COMPLIANCE (Opt-outs are ironclad)
  const isOptOut = systemSettings.optOutKeywords.some(keyword => lowText.includes(keyword.toLowerCase()));

  if (isOptOut) {
    suggestedReply = `Hi ${candidate.name}, we have received your request to stop text updates. We have placed your number (${candidate.phone}) on our permanent do-not-contact list and removed your application from our placement queue.`;
    needsHuman = false; // Auto-sent/confirmed or quick approval
    
    // Auto-blacklist candidate immediately
    candidate.optedOut = true;
    if (!permanentOptOuts.includes(candidate.phone)) {
      permanentOptOuts.push(candidate.phone);
    }
    
    logs.push({
      id: `l-inbound-opt-${Date.now()}`,
      timestamp: new Date().toISOString(),
      level: "warn",
      service: channel === "SMS" ? "sms_poll" : "gmail_listener",
      message: `Inbound Opt-Out detected from ${candidate.name} via ${channel}. Candidate blacklisted immediately.`
    });
  } else if (lowText.includes("yes") || lowText.includes("interested") || lowText.includes("accept")) {
    suggestedReply = `Awesome ${candidate.name}! I've locked you in for the shift. I'm sending the shift confirmation slip to your email. See you there!`;
    needsHuman = false;
    
    // Auto-placed
    candidate.status = "Placed";
    
    logs.push({
      id: `l-inbound-yes-${Date.now()}`,
      timestamp: new Date().toISOString(),
      level: "success",
      service: channel === "SMS" ? "sms_poll" : "gmail_listener",
      message: `${candidate.name} accepted the open shift via ${channel}. Transitioned status to PLACED.`
    });
  } else {
    // Generate simulated AI reply
    suggestedReply = `Hi ${candidate.name}, thank you for your message! Dylan is reviewing your question about "${messageText.substring(0, 30)}...". Let me check with our scheduling desk to confirm details and get back to you immediately.`;
  }

  if (needsHuman) {
    const newItem: ReviewItem = {
      id: `rev-${Date.now()}`,
      candidateId: candidate.id,
      candidateName: candidate.name,
      channel,
      receivedMessage: messageText,
      suggestedReply,
      status: "Pending",
      timestamp: new Date().toISOString()
    };
    reviewQueue.push(newItem);
    
    logs.push({
      id: `l-inbound-review-${Date.now()}`,
      timestamp: new Date().toISOString(),
      level: "info",
      service: channel === "SMS" ? "sms_poll" : "gmail_listener",
      message: `Inbound inquiry from ${candidate.name} requires human-in-the-loop review. Created review item ${newItem.id}.`
    });
  }

  candidate.lastContactDate = new Date().toISOString();

  res.json({ success: true, optedOut: isOptOut, needsReview: needsHuman });
});

// Gemini AI proxy generator using proper @google/genai syntax
app.post("/api/gemini/generate-draft", async (req, res) => {
  const { prompt, candidateName, receivedMessage } = req.body;
  if (!prompt) return res.status(400).json({ error: "Prompt is required" });

  const ai = getGeminiClient();
  if (!ai) {
    // Fallback static generator if API key is missing
    console.warn("Gemini API Key missing. Generating simulated fallback draft.");
    const fallbackTemplates: Record<string, string> = {
      "default": "Hi there! This is Dylan from BlueLine Staffing. Thank you for your message. How can I help you today?",
      "polite": `Hi ${candidateName || "there"}, thank you so much for reaching out to BlueLine Staffing NYC. I have received your response regarding "${receivedMessage || "our active shifts"}". Let me check our registry and coordinate immediately.`,
      "optout": `Hi ${candidateName || "there"}, we understand completely. We have logged your request and have placed your number on our permanent do-not-contact blacklist to cease all communications. We wish you all the best!`
    };
    const draftType = prompt.toLowerCase().includes("optout") || prompt.toLowerCase().includes("blacklist") ? "optout" : (prompt.toLowerCase().includes("polite") ? "polite" : "default");
    return res.json({ text: fallbackTemplates[draftType] });
  }

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: `You are Dylan, the automated nurse recruitment AI representing BlueLine Staffing NYC. 
      You are writing to a nurse candidate named ${candidateName || "Candidate"}. 
      They sent: "${receivedMessage || "Hello"}".
      Generate a professional, warm, and highly clear automated message draft according to this user instruction: "${prompt}".
      Keep the message concise, compliant with TCPA rules (include opt-out instructions if appropriate), and extremely helpful.`
    });

    res.json({ text: response.text });
  } catch (error: any) {
    console.error("Gemini Generation Error:", error);
    res.status(500).json({ error: "Failed to generate draft via Gemini: " + error.message });
  }
});


// Gemini AI Real-time Document Verification Audit
app.post("/api/verify-document", async (req, res) => {
  const { fileName, fileData, mimeType, credentialType, candidateName } = req.body;
  
  const ai = getGeminiClient();
  
  if (!ai) {
    // Dynamic simulated compliance report if Gemini API key is not supplied
    console.warn("Gemini API key missing. Returning high-fidelity audit report simulation.");
    const expiryDate = new Date(Date.now() + 3600000 * 24 * Math.floor(Math.random() * 365 + 180)).toISOString().split('T')[0];
    const docId = "LIC-" + Math.floor(100000 + Math.random() * 900000);
    const checklist = [
      { check: "NYS Registry Verification", passed: true, details: `Verified candidate "${candidateName || 'Lorna Brown'}" name against active New York registry.` },
      { check: "Document Type Integrity", passed: true, details: `Classification matches "${credentialType || 'NYS Nurse License / Registry ID'}".` },
      { check: "Official State Registrar / Seal Match", passed: true, details: "Verified stamp/seal present on digital document." },
      { check: "Signature & Execution Scan", passed: true, details: "Signed and executed appropriately by compliance registrar." },
      { check: "Validation Term Coverage", passed: true, details: `Active and unexpired (Term coverage until ${expiryDate}).` }
    ];

    return res.json({
      verified: true,
      candidateName: candidateName || "Lorna Brown",
      documentType: credentialType || "NYS Nurse License / Registry ID",
      documentId: docId,
      issueDate: "2024-06-15",
      expiryDate: expiryDate,
      authenticityScore: 97,
      checklist,
      notes: `[Sandbox Offline Mode] Successfully validated candidate '${candidateName || 'Lorna Brown'}' credential. Extracted file matches official registrar signatures with high statistical confidence.`,
      auditor: "Dylan AI-Vision-v3.0 (Sandbox-Engine)"
    });
  }

  try {
    let contents: any[] = [];
    
    if (fileData && mimeType) {
      // Real file upload: decode base64 inline data
      contents.push({
        inlineData: {
          mimeType: mimeType,
          data: fileData
        }
      });
      contents.push(`This is a healthcare credential uploaded for candidate "${candidateName || 'Lorna Brown'}".
      Perform an 11-point medical compliance audit on this document. Classify the document type, extract the registration ID, candidate name, issue date, and expiry date. Check if it matches ${credentialType || 'any expected type'}. Ensure it is not expired and is genuine.`);
    } else {
      // Mock / Sample file selected: instruct Gemini to generate high-fidelity audit of this sample name
      contents.push(`Analyze and verify this healthcare staffing credential file:
      - File Name: "${fileName || 'nys_registry_cna_lic.pdf'}"
      - Credential Category: "${credentialType || 'NYS Nurse License / Registry ID'}"
      - Purported Candidate: "${candidateName || 'Lorna Brown'}"
      
      Extract details and evaluate authenticity, validating against New York State healthcare compliance registries (11-point checklist).`);
    }

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: contents,
      config: {
        systemInstruction: `You are Dylan's Document Verification Auditor for BlueLine Staffing NYC. 
        Your job is to analyze medical staffing credentials (licenses, CPR cards, chest x-rays, annual physicals) and verify if they are valid, authentic, and compliant.
        Output a structured JSON response auditing the credential. Assess if the candidate's name matches the document name, if it is expired, if there is a signature or official stamp, and calculate an authenticity score from 0-100. Provide a checklist of 5 criteria verified.`,
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            verified: { type: Type.BOOLEAN, description: "True if document is valid and passes audit" },
            candidateName: { type: Type.STRING, description: "Candidate's name found on document" },
            documentType: { type: Type.STRING, description: "The classified type of document" },
            documentId: { type: Type.STRING, description: "License, ID, or certificate number if found" },
            issueDate: { type: Type.STRING, description: "YYYY-MM-DD issue date of the document" },
            expiryDate: { type: Type.STRING, description: "YYYY-MM-DD expiry date of the document" },
            authenticityScore: { type: Type.INTEGER, description: "Overall confidence score out of 100" },
            checklist: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  check: { type: Type.STRING, description: "Criteria verified" },
                  passed: { type: Type.BOOLEAN, description: "True if this criteria passed" },
                  details: { type: Type.STRING, description: "Detailed findings or extracted text for this check" }
                },
                required: ["check", "passed", "details"]
              }
            },
            notes: { type: Type.STRING, description: "Detailed auditor notes about the document validity and actual use case" },
            auditor: { type: Type.STRING, description: "Dylan Vision 11-pt Auditor signature" }
          },
          required: ["verified", "candidateName", "documentType", "documentId", "issueDate", "expiryDate", "authenticityScore", "checklist", "notes", "auditor"]
        }
      }
    });

    const textVal = response.text ? response.text.trim() : "{}";
    const parsedResult = JSON.parse(textVal);
    res.json(parsedResult);
  } catch (error: any) {
    console.error("Gemini Document Verification Error:", error);
    res.status(500).json({ error: "Failed to audit document: " + error.message });
  }
});


// ==========================================
// VITE OR STATIC FILE SERVING
// ==========================================

async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    // Dev Mode - Boot Vite Dev Server middleware
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    // Production Mode - Serve precompiled files in dist/
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`[Dylan for Hire] Fullstack server running at http://0.0.0.0:${PORT}`);
  });
}

startServer();
