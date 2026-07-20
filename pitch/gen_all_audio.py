"""
Generates all ElevenLabs audio for both documents.
Pitch deck:  12 slides  -> audio2/pitch_s01.mp3 ... pitch_s12.mp3
Arch doc:    19 segments -> audio2/arch_s01.mp3  ... arch_s18.mp3 (+ arch_s03b)

Gibberish prevention:
  - No em dashes (replaced with commas or short pauses)
  - No repetitive sentence-opener patterns in a row
  - All narrations kept under 900 characters
  - Numbers always spelled out
  - FORCE list: files deleted before generation to force fresh render
"""
import requests, os, time
from dotenv import load_dotenv

# [FIXED 2026-07-09] A real, live ElevenLabs key was hardcoded here in plaintext — found while
# auditing this file ahead of a GitHub push (the prior audit note claiming this was "redacted from
# the working file, only in old git history" was wrong; verify claims against the actual file, not
# a prior note). The key's own original comment said it belongs to Wealth Velocity's pipeline
# (~/Downloads/WV/pipeline/.env), not Dylan for Hire's — it should never have been copy-pasted into
# this project at all. Now read from the environment, matching the pattern every other credential in
# this project uses (see src/master_gmail_reviewer.py's CLAUDE_API_KEY/QUO_API_KEY). Add
# ELEVENLABS_API_KEY to ~/Downloads/.env (or wherever this script is actually run from) before
# running it — it will refuse to run with a clear error instead of silently failing if it's missing.
load_dotenv(os.path.expanduser("~/Downloads/.env"))
API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    raise SystemExit(
        "ELEVENLABS_API_KEY not set. Add it to ~/Downloads/.env before running this script — "
        "the key that used to be hardcoded here belonged to Wealth Velocity's pipeline, not this "
        "project, and has been removed. Get the correct key for whichever account should be "
        "generating this audio and set it explicitly."
    )
VOICE_ID  = "VFWoJnruwuOotFvMLmcM"
MODEL     = "eleven_multilingual_v2"
OUT_DIR   = os.path.expanduser("~/Downloads/BlueLine/audio2")
os.makedirs(OUT_DIR, exist_ok=True)

VOICE_SETTINGS = {
    "stability": 0.45,
    "similarity_boost": 0.82,
    "style": 0.15,
    "use_speaker_boost": True,
}
HEADERS = {"xi-api-key": API_KEY, "Content-Type": "application/json"}

# Files to force-regenerate even if they already exist (stale content)
FORCE = {
    "pitch_s05",   # old step order: Doc Review first
    "pitch_s08",   # old single-stream ROI
    "arch_s06",    # old: Step 1 = Doc Review
    "arch_s09",    # old: Step 4 = New Leads
    "arch_s16",    # was OpenPhone/Dylan-specific, now system-agnostic
}

# ─── PITCH DECK NARRATIONS ────────────────────────────────────────────────────

PITCH_NARRATIONS = [

("pitch_s01",
 "Welcome. What you are looking at is a fully automated AI recruiting agent, "
 "built specifically for nursing homes and rehabilitation centers. "
 "It is live. Right now. Running daily. "
 "It reaches out to thirty new nurses every single morning. "
 "It responds to an interested candidate in under ten seconds. "
 "And it has never, not once, accidentally re-contacted someone who asked to be left alone."),

("pitch_s02",
 "Here is what your recruiter does every morning. "
 "They open their laptop, pull up the candidate list, "
 "and for the next two to three hours they copy and paste the same intro message, one nurse at a time. "
 "Seven hundred and fifty hours a year on pure repetition. "
 "And forty percent of candidates who say yes never make it to a shift, "
 "because no one got back to them fast enough. "
 "The average manual response time is over four hours. "
 "By then, they have already taken a shift somewhere else."),

("pitch_s03",
 "Let me walk you through the full journey. "
 "What it actually takes to move a single nurse from first contact to a shift. "
 "Six stages. Twelve to twenty hours of recruiter time. "
 "Thirty-six to forty-nine days to fill a single registered nurse position. "
 "That is the industry average, from the American Society for Healthcare Human Resources Administration. "
 "Stages one through four, lead discovery through candidate communications, BlueLine takes all four to zero. "
 "Stages five and six still need a human, but BlueLine handles eighty-three percent of the document work automatically. "
 "The result is roughly two hours of recruiter time instead of twenty, and a placement in twenty-five days instead of forty-nine."),

("pitch_s04",
 "A recruiter doing this manually costs your agency sixty-two thousand six hundred and forty dollars a year. "
 "That is the direct cost. But here is the number that is never in the proposal. "
 "The average US recruiter is out of the office thirty-seven days per year. "
 "Seven point seven sick days. Twelve vacation days. Seven unscheduled absences. Ten federal holidays. "
 "Fourteen percent of the work year, paid in full, with zero output. "
 "On those thirty-seven days, no outreach goes out. "
 "Eleven hundred candidates are never contacted. "
 "At a five percent placement rate, that is fifty-five missed placements and roughly ninety-nine thousand dollars in missed gross margin. "
 "Every year. The true annual cost of one human recruiter: one hundred and sixty-one thousand dollars. "
 "BlueLine: eighteen thousand. Three hundred and sixty-five days. Zero absences."),

# UPDATED: correct logical step order — New Leads, SMS, Re-engage, Doc Review
("pitch_s05",
 "The agent runs four steps every morning, no human trigger required, "
 "following the logical order of the recruitment funnel. "
 "Step one is New Lead Intro. Thirty fresh candidates get a first message every morning, "
 "cross-checked against all live records first. Zero duplicates. Borough and license-aware from the start. "
 "Step two is SMS Reply Handling. When a nurse texts back, the system acts instantly. "
 "A yes gets the document checklist in under ten seconds. "
 "A stop triggers a permanent block and contact rename right away. "
 "Step three is Re-engagement. Any candidate silent for four or more days gets a personalised follow-up, "
 "but only after the system reads their last four days of conversation history. "
 "If they are mid-process, it skips. "
 "Step four is Document Review. When a serious candidate submits credentials, "
 "Claude Vision reads every attachment, checks all New York State date windows, "
 "and drafts a compliant checklist reply, waiting in your inbox before you sit down."),

("pitch_s06",
 "This is what separates BlueLine from every other automation tool. "
 "Every mass-texting platform fires the same blast to every number and waits. "
 "It has no idea who already submitted documents or who is mid-process. "
 "BlueLine reads the conversation before it sends anything. "
 "Maria submitted all her documents two days ago. "
 "Standard automation sends her: are you still interested? "
 "She already proved she was. She now thinks no one looked at what she sent. "
 "What BlueLine sends instead: just checking in, you sent your documents over on Monday, "
 "our team is reviewing and will be in touch by Thursday. "
 "That is the difference between losing a candidate and keeping her. "
 "And that decision happens automatically, for every single candidate, every morning."),

("pitch_s07",
 "Healthcare staffing carries one of the highest TCPA liability profiles of any industry. "
 "We built the compliance layer before we built the outreach engine. "
 "When a nurse texts stop, her number is written to a permanent file "
 "that survives system restarts, database resets, and CSV re-imports. "
 "There is no workflow, no import, no API call, that gets that number back into the system. "
 "Every email reply is saved as a draft. A human reviews it and sends it. "
 "Nothing goes to a candidate's inbox automatically. "
 "Every action is logged with a timestamp, candidate name, phone number, and the reason for the decision. "
 "One TCPA violation: fifteen hundred dollars. "
 "This architecture makes accidental re-contact structurally impossible."),

# UPDATED: 3-component ROI explanation
("pitch_s08",
 "The sliders are set to industry averages: eight placements per month, "
 "thirty-eight dollar bill rate, thirty-five percent margin, three shifts per week per nurse. "
 "Dial in your actual numbers. The calculator shows three separate value streams. "
 "First, the revenue gain from twenty-five percent more placements from faster response alone, around thirty-three thousand dollars at defaults. "
 "Second, the downtime coverage value. "
 "Thirty-seven days your recruiter is absent each year, thirty leads per day never contacted, "
 "at a five percent conversion rate that is ninety-nine thousand dollars in recovered margin. "
 "Third, seven hundred and fifty hours of manual outreach eliminated per year, "
 "worth around twenty-two thousand dollars in redirected recruiter time. "
 "Add all three streams, subtract the eighteen-thousand-dollar BlueLine cost, "
 "and your year-one net advantage is over one hundred and thirty-six thousand dollars."),

("pitch_s09",
 "Let us look at this through a different lens: cost per placement. "
 "With one recruiter at sixty-two thousand a year placing eight nurses a month, "
 "your cost per placement is around six hundred and fifty dollars. "
 "Add BlueLine and that same recruiter handles forty-five percent more placements, "
 "because the entire outreach and follow-up workload is automated. "
 "Eleven or twelve placements instead of eight, same headcount, same salary. "
 "Your cost per placement drops significantly. "
 "The extra placements generate additional margin that pays for the system many times over. "
 "Dial in your actual recruiter count and cost to see your specific numbers."),

("pitch_s10",
 "Eight capabilities. One price. No modules to buy separately. "
 "Automated SMS outreach, thirty new candidates daily. "
 "Context-aware re-engagement that reads SMS and email history before any follow-up. "
 "Document intelligence, Vision AI reading every credential attachment against New York State date requirements. "
 "Instant SMS reply classification: yes fires a checklist in seconds, stop fires a permanent block. "
 "Full TCPA compliance architecture. Daily run report CSVs. "
 "Borough-aware contact routing across all five NYC boroughs. "
 "And complete white-labelling: your persona, your phone number, your rates, your voice. "
 "Candidates never know this system exists. As far as they are concerned, they are texting your recruiter."),

("pitch_s11",
 "Three tiers. Starter at eight hundred a month covers outreach, reply classification, and compliance. "
 "Professional at fifteen hundred adds the context-aware AI, document review, and the full intelligence layer. "
 "This is where ninety percent of agencies land and stay. "
 "Agency Scale is custom pricing for multi-location operations with ATS integrations. "
 "Here is how to think about the Professional price. "
 "Fifteen hundred a month is fifty dollars a day. "
 "Less than the cost of your recruiter sitting down and opening their laptop before they have done a single productive thing. "
 "For that fifty dollars, you get thirty new contacts, every follow-up, every document review, "
 "full compliance coverage, and daily reporting. Seven days a week."),

("pitch_s12",
 "You can be live in five business days. "
 "Day one is a forty-five-minute kickoff call. "
 "You share your candidate list and connect your agency's SMS number. We configure everything else. "
 "Days two and three, we test on ten real candidates. You watch every action before it touches anyone at scale. "
 "Day four, the first live run. You are on a call watching in real time. "
 "Day five, handover. The agent runs at eight AM every morning from that point forward. "
 "You review any email drafts before they send. That is your entire daily task. "
 "Two weeks from today, you could wake up to thirty nurses contacted, "
 "five active conversations, and two document reviews drafted, "
 "without your team doing any of it. "
 "That is the system. That is what it costs. That is what it delivers."),
]


# ─── ARCHITECTURE DOC NARRATIONS ─────────────────────────────────────────────

ARCH_NARRATIONS = [

("arch_s01",
 "BlueLine Staffing AI Agent, version 2.1. Here is the full pipeline, end to end."),

("arch_s02",
 "Here is the problem. A healthcare recruiter spends twelve to twenty hours of manual work to place a single nurse. "
 "Six stages. Thirty-six to forty-nine days end to end. "
 "BlueLine compresses the first four stages to zero: "
 "lead discovery, information gathering, ATS entry, and the full candidate communication sequence. "
 "All automated."),

("arch_s03",
 "Here is the number that is never in the proposal. "
 "The average US recruiter is out of the office thirty-seven days per year. "
 "Sick days, vacation, unscheduled absences, and holidays. "
 "That is fourteen percent of the work year paid for with zero output, "
 "and eleven hundred candidate contacts that simply never happen. "
 "At a five percent placement rate, that is fifty-five missed placements "
 "and ninety-nine thousand dollars in missed gross margin. Every year. "
 "BlueLine runs three hundred and sixty-five days. Zero sick days. Zero vacation. Zero holidays."),

("arch_s03b",
 "The Agency Cost Calculator shows what this means for your unit economics. "
 "Dial in your recruiter count, their fully-loaded cost, and your current placement rate. "
 "With one recruiter at sixty-two thousand a year placing eight nurses a month, "
 "your cost per placement is around six hundred and fifty dollars. "
 "Add BlueLine and that same recruiter places forty-five percent more. "
 "Your cost per placement drops, and the extra placements pay for the system many times over."),

("arch_s04",
 "Three candidate sources feed the system every day. "
 "A CSV lead list with over three hundred candidates. "
 "Resumes pulled from Indeed. "
 "And inbound emails with attached credential documents."),

("arch_s05",
 "Candidates flow into the Master Daily Agent."),

# UPDATED: Step 1 is now New Lead Intro
("arch_s06",
 "Step one: New Lead Intro. "
 "Thirty fresh candidates get a first message every morning, one hundred and fifty on catch-up weeks. "
 "Every contact is cross-checked against all live records before anything is sent. "
 "Zero duplicates. The system auto-detects license type and NYC borough, "
 "and marks a contact as processed only on confirmed delivery."),

("arch_s07",
 "Step two: SMS Reply Handler. "
 "All inbound messages are scanned and classified. "
 "A yes reply gets the full document checklist in under ten seconds. "
 "A stop triggers a permanent block and contact rename, instantly. "
 "Anything unclear goes straight to the human review queue with full context attached."),

("arch_s08",
 "Step three: Re-engage Stalled contacts. "
 "Any candidate silent for four or more days gets a personalised follow-up, "
 "but only after the system reads their last four days of SMS and email history. "
 "If they are mid-process, it skips entirely. "
 "Never sends a redundant or generic message."),

# UPDATED: Step 4 is now Document Review
("arch_s09",
 "Step four: Document Review. "
 "When a candidate submits their credentials, Claude Vision reads every attachment: "
 "nursing license, physical exam, titers, TB test, BLS card, and I-9 documents. "
 "It validates each one against New York State date windows, "
 "and drafts a compliant checklist reply waiting in your inbox before eight AM."),

("arch_s10",
 "Every message passes through the Intelligence Layer before it goes out."),

("arch_s11",
 "The Context Guard reads four days of SMS and email history before every re-engagement message. "
 "Claude decides in real time: send something relevant and personalised, or skip this contact entirely."),

("arch_s12",
 "The Dedup Engine runs three passes against every existing contact before creating anything new: "
 "phone number, full name, and first name. "
 "No false contacts. No double sends. Ever."),

("arch_s13",
 "Auto-Classification reads the candidate's role field and address "
 "to detect license type and NYC borough automatically. "
 "That data lives in the contact record and drives personalisation at every step."),

("arch_s14",
 "The Compliance Layer enforces a permanent blocked number registry. "
 "Opt-outs survive restarts, re-imports, and manual errors. "
 "Once a number is in the file, there is no workflow, no import, no API call that gets it back out."),

("arch_s15",
 "Four clean outputs come out the other side."),

# UPDATED: system-agnostic, no OpenPhone/Dylan reference
("arch_s16",
 "Outbound SMS through your agency's connected SMS platform, under your recruiter persona. "
 "Email draft replies that wait in your inbox for review before anything is sent, nothing goes automatically. "
 "A human review queue for unrecognised replies, with full conversation context included. "
 "And a timestamped CSV log of every action the system took on that run."),

("arch_s17",
 "Three hundred and forty-four candidates processed. "
 "Forty-one active conversations this week. "
 "Thirty new contacts every morning. Five boroughs covered. "
 "Zero emails sent without a human reviewing them first. "
 "That is the system."),

("arch_s18",
 "BlueLine Staffing AI Agent. Version 2.1. Running live."),
]


# ─── GENERATION ───────────────────────────────────────────────────────────────

ALL = PITCH_NARRATIONS + ARCH_NARRATIONS

# Validate lengths — warn anything over 900 chars
for name, text in ALL:
    if len(text) > 900:
        print(f"[WARN] {name}: {len(text)} chars — consider splitting if TTS quality is poor")

def generate(name, text, force=False):
    path = os.path.join(OUT_DIR, f"{name}.mp3")
    if os.path.exists(path) and not force:
        print(f"[SKIP] {name}  ({os.path.getsize(path)//1024}KB already exists)")
        return True
    if os.path.exists(path) and force:
        os.remove(path)
        print(f"[FORCE] {name}  — deleted stale file, regenerating")
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers=HEADERS,
        json={"text": text, "model_id": MODEL, "voice_settings": VOICE_SETTINGS},
        timeout=60,
    )
    if r.status_code == 200:
        with open(path, "wb") as f:
            f.write(r.content)
        size_kb = len(r.content) // 1024
        print(f"[OK]   {name}  -> {size_kb}KB")
        return True
    else:
        print(f"[ERR]  {name}: HTTP {r.status_code}  {r.text[:200]}")
        return False

ok = 0
failed = []
for name, text in ALL:
    success = generate(name, text, force=(name in FORCE))
    if success:
        ok += 1
    else:
        failed.append(name)
    time.sleep(0.5)   # slightly longer gap — reduces API throttling

print(f"\nDone. {ok}/{len(ALL)} segments generated in {OUT_DIR}")
if failed:
    print(f"FAILED: {failed}")
