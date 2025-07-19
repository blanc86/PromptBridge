from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback  # ✅ Add this for better debugging

from backend.translator import get_translator_instance, unload_translator, translate_to_user_lang
from backend.prompt_optimizer import get_optimized_prompt_and_keywords
from backend.gemini_chat import get_gemini_response
from backend.api_utilities import (
    fetch_weather, fetch_news, fetch_time,
    fetch_quote, fetch_fun_fact, fetch_definition
)
from backend.speech_to_text import run_button_based_transcription, unload_whisper
from backend.text_to_speech import speak

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track current mode
current_mode = {"mode": None}


@app.get("/")
async def read_root():
    return {"message": "Your assistant is up and running!"}


@app.get("/mode")
async def select_mode():
    unload_whisper()
    unload_translator()
    current_mode["mode"] = None
    return {"message": "Select a mode: 'text' or 'voice'"}


@app.post("/set-mode")
async def set_mode(mode_request: dict):
    mode = mode_request.get("mode")
    if mode not in ["text", "voice"]:
        return JSONResponse(status_code=400, content={"error": "Mode must be 'text' or 'voice'"})

    current_mode["mode"] = mode
    return {"message": f"Switched to {mode} mode"}


def get_api_data_summary(prompt: str):
    lower_prompt = prompt.lower()

    try:
        if "weather" in lower_prompt:
            data = fetch_weather(prompt)
            if data:
                return get_gemini_response(f"Summarize the following weather update: {data}")

        elif "news" in lower_prompt:
            data = fetch_news(prompt)
            if data:
                return get_gemini_response(f"Summarize the following news in 3-4 bullet points: {data}")

        elif "time" in lower_prompt:
            data = fetch_time()
            if data:
                return get_gemini_response(f"Summarize the following time and timezone info: {data}")

        elif "quote" in lower_prompt:
            data = fetch_quote()
            if data:
                return data  # Just return the quote directly

        elif "fun fact" in lower_prompt or "fact" in lower_prompt:
            data = fetch_fun_fact()
            if data:
                return data  # Just return the fact directly

        elif "define" in lower_prompt or "definition" in lower_prompt:
            word = lower_prompt.split()[-1]
            data = fetch_definition(word)
            if data:
                return get_gemini_response(f"Explain the definition of '{word}' in simple words: {data}")

        return None
    except Exception as e:
        print("API fetch or summary failed:", e)
        return None


def process_prompt_workflow(user_input: str, source_lang: str):
    translator = get_translator_instance()
    english_prompt = translator.translate_to_english(user_input)

    api_summary = get_api_data_summary(english_prompt)
    if api_summary:
        final_response = translate_to_user_lang(api_summary, source_lang)
        return final_response, []

    if len(english_prompt.strip()) < 300:
        gemini_response = get_gemini_response(english_prompt)
        final_response = translate_to_user_lang(gemini_response, source_lang)
        return final_response, []

    optimized_prompt, keywords = get_optimized_prompt_and_keywords(english_prompt)
    gemini_response = get_gemini_response(optimized_prompt)
    final_response = translate_to_user_lang(gemini_response, source_lang)

    return final_response, keywords


# ✅ Include speak_response toggle in request model
class ChatRequest(BaseModel):
    text: str
    language: str = None
    speak_response: bool = False


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        if current_mode["mode"] != "text":
            return JSONResponse(status_code=400, content={"error": "Current mode is not set to text"})

        user_input = request.text
        if user_input.lower() == "back":
            unload_translator()
            current_mode["mode"] = None
            return {"message": "Returned to mode selection"}

        translator = get_translator_instance()
        source_lang = request.language or translator.detect_lang_code(user_input)
        final_response, keywords = process_prompt_workflow(user_input, source_lang)

        # ✅ Conditional TTS
        if request.speak_response:
            speak(final_response, source_lang)

        return {"response": final_response, "keywords": keywords}

    except Exception as e:
        traceback.print_exc()  # ✅ Print full traceback
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/voice-chat")
async def voice_chat_endpoint():
    try:
        if current_mode["mode"] != "voice":
            return JSONResponse(status_code=400, content={"error": "Current mode is not set to voice"})

        transcribed_text = run_button_based_transcription()
        if not transcribed_text or transcribed_text.lower() == "back":
            unload_whisper()
            unload_translator()
            current_mode["mode"] = None
            return {"message": "Returned to mode selection"}

        translator = get_translator_instance()
        source_lang = translator.detect_lang_code(transcribed_text)
        final_response, keywords = process_prompt_workflow(transcribed_text, source_lang)

        speak(final_response, source_lang)
        unload_whisper()

        return {
            "transcribed_input": transcribed_text,
            "response": final_response,
            "keywords": keywords
        }

    except Exception as e:
        traceback.print_exc()  # ✅ Print full traceback
        return JSONResponse(status_code=500, content={"error": str(e)})
