import asyncio
import os
import sys

VOICE = "en-US-ChristopherNeural"  # Energetic, crystal-clear gaming & stream broadcaster voice
OUTPUT_DIR = "audio"

ANNOUNCEMENTS = [
    ("cta_1", "Double tap on the screen, and subscribe to the channel for more non-stop streams!"),
    ("cta_2", "If you're enjoying the stream, double tap your screen and hit that subscribe button!"),
    ("cta_3", "Don't forget to double tap the screen to support us, and subscribe so you never miss another stream!"),
    ("cta_4", "Double tap the screen to show some love, and subscribe to the channel right now!"),
    ("cta_5", "Double tap that screen right now, and make sure to subscribe to the channel!"),
]

async def generate(edge_tts, text, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
        print(f"[EXISTS] {filename}")
        return
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
    tasks = [generate(edge_tts, text, f"{key}.mp3") for key, text in ANNOUNCEMENTS]

    print(f"Generating {len(tasks)} studio broadcaster call-to-action clips using {VOICE}...")
    await asyncio.gather(*tasks)
    print("Done! All call-to-action voice files are ready in 'audio/' folder.")

if __name__ == "__main__":
    asyncio.run(main())
