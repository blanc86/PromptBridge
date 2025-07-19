# models.py

AVAILABLE_MODELS = {
    "translator": "facebook/nllb-200-distilled-600M",
    "summarizer": "facebook/bart-base",
    "llm": "gemini-1.5-flash-latest",
    "whisper": "openai/whisper-small",
    "gtts": "gTTS (Google Text-to-Speech)"
}

AVAILABLE_APIS = {
    "news": "GNews API",
    "weather": "OpenWeatherMap",
    "time": "TimeZoneDB",
    "quotes": "ZenQuotes",
    "facts": "Useless Facts",
    "dictionary": "DictionaryAPI",
    "stocks": ["Fyers", "Zerodha (Kite)"]
}
