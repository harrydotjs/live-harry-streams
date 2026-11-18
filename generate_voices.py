import asyncio
import os
import sys

VOICE = "en-US-ChristopherNeural"  # High-energy, crisp, clear sports caster voice
OUTPUT_DIR = "audio"

COUNTRIES = [
    ("US", "United States"),
    ("CA", "Canada"),
    ("MX", "Mexico"),
    ("CU", "Cuba"),
    ("JM", "Jamaica"),
    ("BR", "Brazil"),
    ("AR", "Argentina"),
    ("CO", "Colombia"),
    ("CL", "Chile"),
    ("PE", "Peru"),
    ("GB", "United Kingdom"),
    ("FR", "France"),
    ("DE", "Germany"),
    ("IT", "Italy"),
    ("ES", "Spain"),
    ("PT", "Portugal"),
    ("NL", "Netherlands"),
    ("BE", "Belgium"),
    ("CH", "Switzerland"),
    ("SE", "Sweden"),
    ("NO", "Norway"),
    ("DK", "Denmark"),
    ("FI", "Finland"),
    ("IE", "Ireland"),
    ("PL", "Poland"),
    ("AT", "Austria"),
    ("GR", "Greece"),
    ("UA", "Ukraine"),
    ("RU", "Russia"),
    ("HR", "Croatia"),
    ("IN", "India"),
    ("CN", "China"),
    ("JP", "Japan"),
    ("KR", "South Korea"),
    ("KP", "North Korea"),
    ("ID", "Indonesia"),
    ("PK", "Pakistan"),
    ("PH", "Philippines"),
    ("VN", "Vietnam"),
    ("TH", "Thailand"),
    ("SG", "Singapore"),
    ("SA", "Saudi Arabia"),
    ("AE", "United Arab Emirates"),
    ("IL", "Israel"),
    ("TR", "Turkey"),
    ("EG", "Egypt"),
    ("ZA", "South Africa"),
    ("MA", "Morocco"),
    ("AU", "Australia"),
    ("NZ", "New Zealand"),
]

MILESTONES = {
    "m_start": "Welcome to the clash! Fifty countries. One champion.",
    "m_duel": "The final duel! Two countries remain!",
    "m_top5": "The final five! Which nation will become champion?",
    "m_top10": "Only ten countries remaining!",
    "m_top25": "Only twenty-five countries remaining!",
    "m_cta1": "Double tap on the screen if your country is still alive, and comment down your country!",
    "m_cta2": "Comment down your country right now, and double tap the screen to support your nation!",
}

sem = asyncio.Semaphore(10)

async def generate(edge_tts, text, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
        return
    async with sem:
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(text, VOICE, rate="+3%", pitch="+0Hz")
                await communicate.save(filepath)
                print(f"[OK] {filename}: {text}")
                return
            except Exception as e:
                print(f"[Retry {attempt+1}] {filename}: {e}")
                await asyncio.sleep(1)

async def main():
    try:
        import edge_tts
    except ImportError:
        print("edge-tts not installed. Run: pip install edge-tts")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tasks = []

    # 1. Elimination announcements (e.g. 'United States eliminated!')
    for code, name in COUNTRIES:
        tasks.append(generate(edge_tts, f"{name} eliminated!", f"c_{code}.mp3"))

    # 2. Champion celebrations
    for code, name in COUNTRIES:
        tasks.append(generate(edge_tts, f"Your World Clash Fight champion is {name}! What a legendary victory!", f"win_{code}.mp3"))

    # 3. Game milestones & engagement prompts
    for key, text in MILESTONES.items():
        tasks.append(generate(edge_tts, text, f"{key}.mp3"))

    print(f"Generating {len(tasks)} ultra-clear broadcast voice clips using {VOICE}...")
    await asyncio.gather(*tasks)
    print("Done! All announcer voice files are ready in 'audio/' folder.")

if __name__ == "__main__":
    asyncio.run(main())
