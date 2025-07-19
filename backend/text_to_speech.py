from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from langdetect import detect
import io

def speak(text: str, lang: str = None):
    # Converts text to speech, detecting language if not specified
    if lang is None:
        lang = detect(text)
    try:
        tts = gTTS(text=text, lang=lang)
        with io.BytesIO() as f:
            tts.write_to_fp(f)
            f.seek(0)
            audio = AudioSegment.from_file(f, format="mp3")
            play(audio)
    except ValueError:
        print(f"❌ Language '{lang}' not supported by gTTS.")

def stop_speaking():
    global current_playback
    if current_playback:
        current_playback.stop()
        current_playback = None

# Only runs when the file is executed directly
if __name__ == "__main__":
    # Example: Speak a phrase in any detectable language
    speak("तुम्हारा नाम क्या है?")
    speak("What is your name?")
    speak("আপনার নাম কি?")
    
# Final Copy