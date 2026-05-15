import os
from google import genai
from google.genai import types
from moviepy.editor import VideoFileClip

# --- CONFIGURATION ---
API_KEY = "Your Gemini API Key"
INPUT_VIDEO = "input.mp4"
OUTPUT_SUBTITLE = "khmer.vtt"

client = genai.Client(api_key=API_KEY)

def run():
    print(f"Step 1: Extracting Audio from {INPUT_VIDEO}...")
    video = VideoFileClip(INPUT_VIDEO)
    video.audio.write_audiofile("temp_sub.mp3", logger=None) 

    print("Step 2: Listening & Generating Khmer Subtitles (WebVTT)...")
    with open("temp_sub.mp3", "rb") as f:
        audio_bytes = f.read()

    # A highly strict prompt to prevent the AI from grouping text into giant blocks
    strict_vtt_prompt = """
    Listen to the English audio and translate it into Khmer.
    You MUST output the result as a strictly formatted WebVTT (.vtt) file.
    
    CRITICAL RULES:
    1. The very first line MUST be exactly: WEBVTT
    2. Do NOT output the original English transcript. Only output the translated Khmer text.
    3. You MUST break the translation down into short, readable subtitle blocks (roughly 3 to 7 seconds per block).
    4. Do NOT group all the text into one giant timestamp. Create a continuous, chronological sequence of timestamps.
    
    FORMAT EXAMPLE:
    WEBVTT
    
    00:00:00.000 --> 00:00:04.500
    [First sentence of Khmer text here]
    
    00:00:04.500 --> 00:00:08.200
    [Next sentence of Khmer text here]
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3"),
            strict_vtt_prompt
        ]
    )
    
    if not response.candidates or not response.text:
        print("\n[!] ERROR: Gemini returned no text. The audio may be silent.")
        return

    # Clean up the output to ensure it's a perfectly valid VTT file
    vtt_content = response.text.strip()
    vtt_content = vtt_content.replace("```vtt", "").replace("```", "").strip()
    
    # Failsafe: Browsers reject the file if it doesn't start with WEBVTT
    if not vtt_content.startswith("WEBVTT"):
        vtt_content = "WEBVTT\n\n" + vtt_content

    print(f"Step 3: Saving Subtitles to {OUTPUT_SUBTITLE}...")
    with open(OUTPUT_SUBTITLE, "w", encoding="utf-8") as f:
        f.write(vtt_content)

    print("Step 4: Generating Web Player (index.html)...")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Khmer Subtitles Player</title>
    </head>
    <body style="background:#111; color:white; font-family:sans-serif; text-align:center; padding:20px;">
        <h2>Original Video with Khmer Subtitles</h2>
        <video controls width="100%" style="max-width: 800px; border: 2px solid #444; border-radius: 8px;" crossorigin="anonymous">
            <source src="{INPUT_VIDEO}" type="video/mp4">
            <track label="Khmer" kind="subtitles" srclang="km" src="{OUTPUT_SUBTITLE}" default>
        </video>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\nSuccess! Subtitle file saved as {OUTPUT_SUBTITLE}")
    
    # Print a quick preview to verify chunking
    print("\n--- Subtitle Preview ---")
    preview_lines = vtt_content.split('\n')[:12]
    print('\n'.join(preview_lines) + "\n...")
    print("------------------------\n")

    if os.path.exists("temp_sub.mp3"):
        os.remove("temp_sub.mp3")

if __name__ == "__main__":
    run()
