import asyncio
import os
import sys

VOICE = "en-US-ChristopherNeural"  # Energetic, crystal-clear gaming & stream broadcaster voice
OUTPUT_DIR = "audio"

ANNOUNCEMENTS = [
    ("cta_1", "Double tap on the screen, and subscribe to the channel for more non-stop streams!"),
    ("cta_2", "If you're enjoying the stream, double tap your screen and hit that subscribe button!"),
    ("cta_3", "Don't forget to double tap the screen to support us, and subscribe so you never miss another stream!"),
    ("cta_4", "like the stream, and subscribe to the channel right now!"),
    ("cta_5", "Hit a like, and make sure to subscribe to the channel!"),
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

    # Assemble into seamless 5-minute repeating loop (1 announcement every 60s)
    build_announcements_loop()

def build_announcements_loop():
    import subprocess
    clips = [f"audio/{key}.mp3" for key, _ in ANNOUNCEMENTS]
    available = [c for c in clips if os.path.exists(c) and os.path.getsize(c) > 500]
    if not available:
        print("[Warning] No voice clips available to compile.")
        return

    cmd = ["ffmpeg", "-y"]
    filter_inputs = []
    for i, clip in enumerate(available):
        cmd.extend(["-i", clip])
        delay_ms = (15 + i * 60) * 1000  # 15s, 75s, 135s, 195s, 255s...
        filter_inputs.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[a{i}];")

    mix_str = "".join([f"[a{i}]" for i in range(len(available))])
    total_dur = max(60 * len(available), 300)
    filter_complex = "".join(filter_inputs) + f"{mix_str}amix=inputs={len(available)}:duration=longest[amix];[amix]apad=whole_dur={total_dur}[aout]"

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "announcements_loop.mp3"
    ])

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[OK] Generated repeating announcement loop: announcements_loop.mp3 ({total_dur}s)")
    except Exception as e:
        print(f"[Notice] FFmpeg announcement compilation notice: {e}")

if __name__ == "__main__":
    asyncio.run(main())
