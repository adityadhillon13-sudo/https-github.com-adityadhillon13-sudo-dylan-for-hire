"""
Embeds ElevenLabs MP3 audio into both HTML files as base64-encoded Audio objects.
Replaces the Web Speech API narration functions with ElevenLabs audio playback.
"""
import base64, os

AUDIO_DIR = os.path.expanduser("~/Downloads/BlueLine/audio2")
BL_DIR    = os.path.expanduser("~/Downloads/BlueLine")


def read_b64(filename):
    path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(path):
        print(f"  [MISSING] {filename}")
        return None
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    size_kb = os.path.getsize(path) // 1024
    b64_kb  = len(data) // 1024
    print(f"  [OK] {filename}  {size_kb}KB -> {b64_kb}KB base64")
    return f"data:audio/mpeg;base64,{data}"


# ─── PITCH DECK ───────────────────────────────────────────────────────────────
print("\n=== Pitch Deck (slides 1-12) ===")

pitch_files = [f"pitch_s{k:02d}.mp3" for k in range(1, 13)]
pitch_srcs  = []
for fn in pitch_files:
    pitch_srcs.append(read_b64(fn) or "null")

# JS: AUDIO_FILES object keyed 1-12
lines = ["const AUDIO_FILES = {"]
for k, src in enumerate(pitch_srcs, start=1):
    if src == "null":
        lines.append(f"  {k}: null,")
    else:
        lines.append(f"  {k}: '{src}',")
lines.append("};")
PITCH_AUDIO_DEF = "\n".join(lines)

# Replace both the NAR array, synth setup, playNarration, and toggleNarration
PITCH_OLD_MARKER_START = "const NAR=["
PITCH_OLD_MARKER_END   = "synth.getVoices();\nrenderNotes(1);calcROI();calcCPP();"

PITCH_NEW_NARRATION = (
    PITCH_AUDIO_DEF + """

let _pa = null;
function playNarration(n){
  if(!narrationOn) return;
  if(_pa){ _pa.pause(); _pa.currentTime=0; _pa=null; }
  const src = AUDIO_FILES[n];
  if(!src) return;
  _pa = new Audio(src);
  _pa.play().catch(()=>{});
}
function toggleNarration(){
  narrationOn = !narrationOn;
  const btn = document.getElementById('narrationBtn');
  if(!narrationOn){
    btn.textContent = '🔇 Narration Off';
    btn.style.background = 'var(--dim)';
    if(_pa){ _pa.pause(); _pa.currentTime=0; _pa=null; }
  } else {
    btn.textContent = '🔊 Narration On';
    btn.style.background = 'var(--blue)';
  }
}
renderNotes(1);calcROI();calcCPP();"""
)

pitch_path = os.path.join(BL_DIR, "blueline_pitch_deck.html")
with open(pitch_path, "r", encoding="utf-8") as f:
    html = f.read()

start_i = html.find(PITCH_OLD_MARKER_START)
end_i   = html.find(PITCH_OLD_MARKER_END)
if start_i == -1 or end_i == -1:
    print("  [WARN] Could not find exact markers — attempting fallback injection")
    # Fallback: inject before last </script>
    html = html.replace("</script>\n</body>",
                        PITCH_AUDIO_DEF + "\n" + PITCH_NEW_NARRATION + "\n</script>\n</body>", 1)
else:
    end_i += len(PITCH_OLD_MARKER_END)
    html = html[:start_i] + PITCH_NEW_NARRATION + html[end_i:]
    print("  [REPLACED] Web Speech API narration block")

with open(pitch_path, "w", encoding="utf-8") as f:
    f.write(html)
size_mb = os.path.getsize(pitch_path) / (1024 * 1024)
print(f"  Saved: {pitch_path}  ({size_mb:.1f} MB)")


# ─── ARCHITECTURE DOC ─────────────────────────────────────────────────────────
print("\n=== Architecture Doc (19 segments) ===")

# Keys match SEGMENTS array order (0-indexed → files listed in order)
arch_segment_files = [
    "arch_s01.mp3",   # idx 0
    "arch_s02.mp3",   # idx 1
    "arch_s03.mp3",   # idx 2
    "arch_s03b.mp3",  # idx 3
    "arch_s04.mp3",   # idx 4
    "arch_s05.mp3",   # idx 5
    "arch_s06.mp3",   # idx 6  — Step 1 New Leads
    "arch_s07.mp3",   # idx 7  — Step 2 SMS
    "arch_s08.mp3",   # idx 8  — Step 3 Re-engage
    "arch_s09.mp3",   # idx 9  — Step 4 Doc Review
    "arch_s10.mp3",   # idx 10
    "arch_s11.mp3",   # idx 11
    "arch_s12.mp3",   # idx 12
    "arch_s13.mp3",   # idx 13
    "arch_s14.mp3",   # idx 14
    "arch_s15.mp3",   # idx 15
    "arch_s16.mp3",   # idx 16
    "arch_s17.mp3",   # idx 17
    "arch_s18.mp3",   # idx 18
]

arch_srcs = []
for fn in arch_segment_files:
    arch_srcs.append(read_b64(fn) or "null")

lines = ["const ARCH_AUDIO = ["]
for src in arch_srcs:
    if src == "null":
        lines.append("  null,")
    else:
        lines.append(f"  '{src}',")
lines.append("];")
ARCH_AUDIO_DEF = "\n".join(lines)

# Replace the speak() function and synth setup
ARCH_OLD_SPEAK = """/* Web Speech API narration */
function speak(text,onEnd){
  synth.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.rate=0.92;u.pitch=1.0;u.volume=1;
  const voices=synth.getVoices();
  const preferred=voices.find(v=>v.name.includes('Samantha')||v.name.includes('Google US English')||v.lang==='en-US');
  if(preferred)u.voice=preferred;
  u.onend=()=>{if(onEnd)onEnd();};
  u.onerror=()=>{if(onEnd)onEnd();};
  synth.speak(u);
}"""

ARCH_NEW_SPEAK = """/* ElevenLabs audio playback */
let _aa = null;
function speak(text, onEnd, segIdx){
  if(_aa){ _aa.pause(); _aa.currentTime=0; _aa=null; }
  const src = (typeof segIdx !== 'undefined' && ARCH_AUDIO[segIdx]) ? ARCH_AUDIO[segIdx] : null;
  if(!src){ if(onEnd) onEnd(); return; }
  _aa = new Audio(src);
  _aa.onended = ()=>{ _aa=null; if(onEnd) onEnd(); };
  _aa.onerror = ()=>{ _aa=null; if(onEnd) onEnd(); };
  _aa.play().catch(()=>{ if(onEnd) onEnd(); });
}"""

# Also replace the playSegment call to pass idx to speak()
ARCH_OLD_PLAYSEG = "  speak(SEGMENTS[idx].nar,()=>{"
ARCH_NEW_PLAYSEG = "  speak(SEGMENTS[idx].nar,()=>{/* */},idx); speak._cb=()=>{"

# Simpler: patch the speak() call signature directly
ARCH_OLD_PLAYSEG2 = "  speak(SEGMENTS[idx].nar,()=>{\n    if(playing)playSegment(idx+1);\n  });"
ARCH_NEW_PLAYSEG2 = "  speak(SEGMENTS[idx].nar,()=>{\n    if(playing)playSegment(idx+1);\n  }, idx);"

# Replace synth.cancel() calls with audio stop
ARCH_OLD_SYNTH1 = "playing=false;synth.cancel();\n    document.getElementById('playBtn').textContent='▶ Play';"
ARCH_NEW_SYNTH1 = "playing=false; if(_aa){_aa.pause();_aa.currentTime=0;_aa=null;}\n    document.getElementById('playBtn').textContent='▶ Play';"

ARCH_OLD_SYNTH2 = "playing=false;synth.cancel();\n  clearAll();"
ARCH_NEW_SYNTH2 = "playing=false; if(_aa){_aa.pause();_aa.currentTime=0;_aa=null;}\n  clearAll();"

ARCH_OLD_SYNTH_INIT = "const synth=window.speechSynthesis;"
ARCH_NEW_SYNTH_INIT = ""  # remove

ARCH_OLD_VOICES = """if(synth.onvoiceschanged!==undefined)synth.onvoiceschanged=()=>synth.getVoices();
synth.getVoices();"""
ARCH_NEW_VOICES = ""  # remove

arch_path = os.path.join(BL_DIR, "blueline_architecture_doc.html")
with open(arch_path, "r", encoding="utf-8") as f:
    html = f.read()

# Inject audio data right before </script>
html = html.replace(
    "</script>\n</body>",
    ARCH_AUDIO_DEF + "\n</script>\n</body>",
    1
)
print("  [INJECTED] ARCH_AUDIO array")

# Apply all replacements
replacements = [
    (ARCH_OLD_SYNTH_INIT,    ARCH_NEW_SYNTH_INIT),
    (ARCH_OLD_SPEAK,         ARCH_NEW_SPEAK),
    (ARCH_OLD_PLAYSEG2,      ARCH_NEW_PLAYSEG2),
    (ARCH_OLD_SYNTH1,        ARCH_NEW_SYNTH1),
    (ARCH_OLD_SYNTH2,        ARCH_NEW_SYNTH2),
    (ARCH_OLD_VOICES,        ARCH_NEW_VOICES),
]

for old, new in replacements:
    if old in html:
        html = html.replace(old, new, 1)
        label = old.split("\n")[0][:60]
        print(f"  [REPLACED] {label!r}")
    else:
        label = old.split("\n")[0][:60]
        print(f"  [SKIP/NOT FOUND] {label!r}")

with open(arch_path, "w", encoding="utf-8") as f:
    f.write(html)
size_mb = os.path.getsize(arch_path) / (1024 * 1024)
print(f"  Saved: {arch_path}  ({size_mb:.1f} MB)")

print("\nAll done. Open both HTML files and click Play / Auto-Play to verify audio.")
