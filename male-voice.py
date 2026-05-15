import os
import wave
from google import genai
from google.genai import types
from moviepy.editor import VideoFileClip, AudioFileClip

# --- CONFIGURATION ---
API_KEY = "Your Gemini API Key"
INPUT_VIDEO = "input.mp4"
OUTPUT_VIDEO = "khmer_output.mp4"

client = genai.Client(api_key=API_KEY)

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def run():
    print("Step 1: Extracting Audio from video...")
    video = VideoFileClip(INPUT_VIDEO)
    video.audio.write_audiofile("temp.mp3", logger=None) 

    print("Step 2: Listening & Translating to Khmer...")
    with open("temp.mp3", "rb") as f:
        audio_bytes = f.read()

    trans_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3"),
            "Listen to the spoken English in this audio and translate it into Khmer. Return only the translated Khmer text."
        ]
    )
    
    if not trans_response.candidates or not trans_response.text:
        print("\n[!] ERROR: Gemini returned no text. The audio is either silent or blocked.")
        return

    khmer_text = trans_response.text.strip()
    print(f"\n--- Translated Script Preview ---\n{khmer_text}\n---------------------------------\n")

    print("Step 3: Generating Custom AI Studio Voice (Enceladus)...")
    
    # Your custom directorial prompt injected with the dynamic Khmer translation
    custom_prompt = f"""Read the following transcript based on the audio profile and director's note.

# Audio Profile
A helpful and professional personal male Cambodian speaker 

# Director's note
Style: Professional, authoritative, clear articulation with standard broadcast cadence. Pace: Natural. Accent: Neutral.

## Scene:
A quiet, professional remote workspace.

## Sample Context:
Steady, efficient, and male speaker

## Transcript:
{khmer_text}"""

    tts_response = client.models.generate_content(
       model="gemini-3.1-flash-tts-preview",
       contents=[
           types.Content(
               role="user",
               parts=[types.Part.from_text(text=custom_prompt)]
           )
       ],
       config=types.GenerateContentConfig(
          temperature=1.05, # Your custom temperature
          response_modalities=["AUDIO"],
          speech_config=types.SpeechConfig(
             voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                   voice_name="Enceladus", # Your custom male voice
                )
             )
          ),
       )
    )

    print("Step 4: Saving .wav & Muxing back to video...")
    pcm_data = tts_response.candidates[0].content.parts[0].inline_data.data
    wave_file('khmer.wav', pcm_data)

    khmer_audio = AudioFileClip("khmer.wav")
    final_video = video.set_audio(khmer_audio)
    final_video.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", logger=None)
    
    print(f"\nSuccess! Translated video saved as {OUTPUT_VIDEO}")

    for file in ["temp.mp3", "khmer.wav"]:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    run()
