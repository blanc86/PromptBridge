import sounddevice as sd
import numpy as np
import threading
from faster_whisper import WhisperModel
from typing import Optional
import torch
import time

# Audio parameters
sample_rate = 16000
block_duration = 5  # seconds

# Global model (lazy-loaded)
model = None

# Globals
final_transcript = []
stop_recording = threading.Event()
is_recording = False

def load_whisper():
    """Load the Whisper model if not already loaded"""
    global model
    if model is None:
        print("🎤 Loading Whisper model...")
        model = WhisperModel("medium", compute_type="float16", device="cuda")
        print("✅ Whisper model loaded.")

def unload_whisper():
    """Unload the Whisper model and free GPU memory"""
    global model
    if model:
        print("🧹 Unloading Whisper model...")
        del model
        model = None
        torch.cuda.empty_cache()
        print("✅ Whisper model unloaded.")

def transcribe_block():
    """Record and transcribe a block of audio"""
    global model
    audio = sd.rec(int(sample_rate * block_duration), samplerate=sample_rate, channels=1)
    sd.wait()
    audio_array = np.squeeze(audio)

    if not np.any(audio_array):
        print("⚠️ Skipping silent audio block")
        return

    print("📡 Transcribing...")
    segments_gen, _ = model.transcribe(
        audio_array,
        language=None,
        beam_size=10,
        vad_filter=True,
        vad_parameters={"threshold": 0.5}
    )

    for segment in segments_gen:
        text = segment.text.strip()
        if text:
            print(f"🗣️ {text}")
            final_transcript.append(text)

def record_loop():
    """Continuous recording and transcription loop"""
    global is_recording
    is_recording = True
    print("\n🎤 Recording started. Speak now!")
    
    while not stop_recording.is_set():
        transcribe_block()
    
    is_recording = False
    print("\n🛑 Recording stopped.")

def start_recording():
    """Start the recording process - called from Streamlit button"""
    global final_transcript, stop_recording
    
    # Reset transcript and flag
    final_transcript = []
    stop_recording.clear()
    
    # Load model if needed
    load_whisper()
    
    # Start recording in a separate thread
    recording_thread = threading.Thread(target=record_loop)
    recording_thread.daemon = True  # Make thread exit when main program exits
    recording_thread.start()
    
    # Give the thread a moment to start
    time.sleep(0.5)
    
    return True

def stop_recording_and_transcribe():
    """Stop recording and return the transcript - called from Streamlit button"""
    global stop_recording, final_transcript
    
    if is_recording:
        stop_recording.set()
        # Wait briefly for recording to complete
        time.sleep(0.5)
        
        # Combine all transcribed segments
        full_transcript = " ".join(final_transcript)
        print("\n📝 Final Transcript:")
        print(full_transcript)
        
        return full_transcript
    else:
        print("⚠️ No active recording to stop")
        return ""

def run_button_based_transcription():
    """
    Legacy function for compatibility with Streamlit code
    Now acts as a wrapper around start_recording() and returns an empty string
    Actual transcription will be fetched via stop_recording_and_transcribe()
    """
    start_recording()
    # Return empty string - Streamlit will call stop_recording_and_transcribe() later
    return ""

def check_recording_status():
    """Return True if currently recording, False otherwise"""
    return is_recording

# If run directly as a script for testing
if __name__ == "__main__":
    try:
        print("Testing speech-to-text module...")
        print("Press Ctrl+C to exit")
        start_recording()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping recording...")
        transcript = stop_recording_and_transcribe()
        print(f"Final transcript: {transcript}")
        unload_whisper()