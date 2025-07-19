import streamlit as st
import sys
import os
import time
# Add the parent directory to the Python path to allow importing modules from the parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.translator import get_translator_instance, unload_translator, translate_to_user_lang
from backend.prompt_optimizer import get_optimized_prompt_and_keywords
from backend.gemini_chat import get_gemini_response
from backend.api_utilities import (
    fetch_weather, fetch_news, fetch_time,
    fetch_quote, fetch_fun_fact, fetch_definition
)
from backend.speech_to_text import run_button_based_transcription, unload_whisper
from backend.speech_to_text import start_recording, stop_recording_and_transcribe, check_recording_status, unload_whisper
from backend.text_to_speech import speak, stop_speaking
import traceback

# App configuration
st.set_page_config(
    page_title="PromptBridge AI Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Initialization
if "mode" not in st.session_state:
    st.session_state.mode = "text"
if "transcribed_input" not in st.session_state:
    st.session_state.transcribed_input = ""
if "recording" not in st.session_state:
    st.session_state.recording = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_response" not in st.session_state:
    st.session_state.current_response = ""
if "response_times" not in st.session_state:
    st.session_state.response_times = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# CSS Styling
st.markdown("""
    <style>
        /* Global Styling */
        [data-testid="stAppViewContainer"] {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #1a1c24;
            padding: 2rem 1rem;
            border-right: 1px solid #2d2d2d;
        }
        
        /* Main Content Styling */
        .main .block-container {
            padding: 2rem 3rem 3rem;
        }
        
        /* Header Styling */
        h1, h2, h3 {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            font-weight: 600;
            color: #f0f0f0;
        }
        
        /* Card Container for Chat */
        .chat-container {
            background-color: #1e2130;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #2d3748;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        /* Message Bubbles */
        .user-message {
            background-color: #3730a3;
            color: white;
            padding: 12px 18px;
            border-radius: 18px 18px 0 18px;
            margin: 10px 0;
            display: inline-block;
            max-width: 80%;
            float: right;
            clear: both;
        }
        
        .assistant-message {
            background-color: #2d3748;
            color: white;
            padding: 12px 18px;
            border-radius: 18px 18px 18px 0;
            margin: 10px 0;
            display: inline-block;
            max-width: 80%;
            float: left;
            clear: both;
        }
        
        /* Text Input Styling */
        .stTextArea textarea {
            background-color: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 10px;
            padding: 12px;
            color: white;
            font-size: 16px;
        }
        
        /* Button Styling */
        .primary-button {
            background-color: #6c63ff;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .primary-button:hover {
            background-color: #5a51db;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .secondary-button {
            background-color: #3d4a5c;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .secondary-button:hover {
            background-color: #4a5568;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        /* Mode Selection Styling */
        .mode-selector {
            background-color: #2d3748;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        /* Checkbox Styling */
        .stCheckbox label {
            color: #c7d2fe;
            font-size: 16px;
        }
        
        /* Tab Navigation */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #2d3748;
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #6c63ff;
        }
        
        /* Recording Indicator */
        .recording-active {
            color: #ef4444;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        /* Divider */
        hr {
            border: 0;
            height: 1px;
            background-color: #4a5568;
            margin: 1.5rem 0;
        }
        
        /* Status Info */
        .status-info {
            background-color: #2d3748;
            border-radius: 8px;
            padding: 12px;
            margin-top: 12px;
            border-left: 4px solid #6c63ff;
        }
        
        /* Utility Classes */
        .center-text {
            text-align: center;
        }
        
        .flex-container {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        /* Response Container */
        .response-container {
            background-color: #2d3748;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            border-left: 4px solid #6c63ff;
        }
        
        /* Response Time Badge */
        .response-time {
            font-size: 0.75em;
            color: #a0aec0;
            background-color: #2d3748;
            border-radius: 8px;
            padding: 2px 8px;
            float: right;
            margin-top: 5px;
        }
        
        /* Clear floats */
        .clearfix::after {
            content: "";
            clear: both;
            display: table;
        }
    </style>
""", unsafe_allow_html=True)

# Function to simulate typing 's' or 'e' in the terminal for Windows using os.system()
# def send_terminal_input(command: str):
#     try:
#         if sys.platform == "win32":
#             os.system(f'echo {command}')
#         else:
#             os.system(f'echo {command} > /dev/tty')
#     except Exception as e:
#         st.error(f"Failed to send command to terminal: {e}")

def extract_city_name(prompt):
    known_cities = [
        "Delhi", "Mumbai", "Bengaluru", "Chennai", "Kolkata", "Hyderabad", "Pune",
        "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal",
        "Patna", "Vadodara", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
        "Rajkot", "Varanasi", "Srinagar", "Amritsar", "Prayagraj", "Ranchi",
        "Howrah", "Gwalior", "Jodhpur", "Coimbatore", "Vijayawada", "Jabalpur",
        "Madurai", "Raipur", "Kota", "Guwahati", "Chandigarh", "Solapur", "Hubli",
        "Mysore", "Tiruchirappalli", "Bareilly", "Moradabad", "Thiruvananthapuram",
        "Noida", "Ghaziabad", "Visakhapatnam", "Davangere", "Mangalore", "Salem"
    ]

    for city in known_cities:
        if city.lower() in prompt.lower():
            return city
    return None


# Function to get summaries from APIs
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
            return fetch_quote()

        elif "fun fact" in lower_prompt or "fact" in lower_prompt:
            return fetch_fun_fact()

        elif "define" in lower_prompt or "definition" in lower_prompt:
            word = lower_prompt.split()[-1]
            data = fetch_definition(word)
            if data:
                return get_gemini_response(f"Explain the definition of '{word}' in simple words: {data}")

        return None
    except Exception as e:
        st.error(f"API fetch or summary failed: {e}")
        return None

# Function to process prompt
def process_prompt_workflow(user_input: str, source_lang: str):
    if not user_input.strip():
        return "Please provide a message.", []

    # Skip translation if input is in English
    if source_lang == "en":
        english_prompt = user_input
    else:
        translator = get_translator_instance()
        english_prompt = translator.translate_to_english(user_input)

    api_summary = get_api_data_summary(english_prompt)
    if api_summary:
        # Remove any '*' symbols from response
        api_summary = api_summary.replace('*', '')
        # Only translate back if original input was not in English
        if source_lang == "en":
            final_response = api_summary
        else:
            final_response = translate_to_user_lang(api_summary, source_lang)
        return final_response, []

    if len(english_prompt.strip()) < 300:
        gemini_response = get_gemini_response(english_prompt)
        # Remove any '*' symbols from response
        gemini_response = gemini_response.replace('*', '')
        # Only translate back if original input was not in English
        if source_lang == "en":
            final_response = gemini_response
        else:
            final_response = translate_to_user_lang(gemini_response, source_lang)
        return final_response, []

    optimized_prompt, keywords = get_optimized_prompt_and_keywords(english_prompt)
    gemini_response = get_gemini_response(optimized_prompt)
    # Remove any '*' symbols from response
    gemini_response = gemini_response.replace('*', '')
    # Only translate back if original input was not in English
    if source_lang == "en":
        final_response = gemini_response
    else:
        final_response = translate_to_user_lang(gemini_response, source_lang)

    return final_response, keywords


# Function to handle user input
def handle_user_input(user_input: str, speak_response: bool = False):
    if not user_input.strip():
        return
        
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    try:
        # Start the timer
        start_time = time.time()
        
        # Process the user's message
        translator = get_translator_instance()
        source_lang = translator.detect_lang_code(user_input)
        final_response, keywords = process_prompt_workflow(user_input, source_lang)
        
        # Calculate the response time
        end_time = time.time()
        response_time = round(end_time - start_time, 2)
        
        # Add response time to history
        st.session_state.response_times.append(response_time)
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": final_response,
            "keywords": keywords if keywords else [],
            "response_time": response_time
        })
        
        # Text-to-speech if enabled
        if speak_response:
            speak(final_response, source_lang)
            
        st.session_state.current_response = final_response
        
        # Clear the input field after sending
        st.session_state.user_input = ""
            
    except Exception as e:
        traceback.print_exc()
        st.error(f"Error: {str(e)}")

# Calculate average response time
def get_average_response_time():
    if not st.session_state.response_times:
        return 0
    return round(sum(st.session_state.response_times) / len(st.session_state.response_times), 2)

# Callback function for input field
def on_input_change():
    st.session_state.user_input = st.session_state.text_input

# Callback function for send button
def on_send_button_click():
    user_input = st.session_state.user_input
    speak_response = st.session_state.speak_text_response
    handle_user_input(user_input, speak_response)

# Sidebar - Navigation and Controls
with st.sidebar:
    st.image("backend\AI assistant.jpg", width=120)
    st.title("AI Assistant")
    
    st.markdown("### Interaction Mode")
    mode = st.radio(
        "Choose how to interact:",
        ["Text Mode", "Voice Mode"],
        index=0 if st.session_state.mode == "text" else 1,
        key="interaction_mode"
    )
    
    # Update session state based on sidebar selection
    if mode == "Text Mode":
        st.session_state.mode = "text"
    else:
        st.session_state.mode = "voice"
    
    st.markdown("---")
    
    # Performance metrics
    st.markdown("### Performance Metrics")
    if st.session_state.response_times:
        last_response_time = st.session_state.response_times[-1]
        avg_response_time = get_average_response_time()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Last Response", f"{last_response_time}s")
        with col2:
            st.metric("Average", f"{avg_response_time}s")
    else:
        st.info("No responses yet")
    
    st.markdown("---")
    
    # Additional sidebar controls
    with st.expander("About", expanded=False):
        st.markdown("""
        **PromptBridge AI Assistant**
        
        This assistant can:
        - Understand and respond in multiple languages
        - Process voice input and provide voice output
        - Answer general questions and provide information
        """)
    
    # Reset conversation button
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_response = ""
        st.session_state.response_times = []
        st.rerun()

# Main Content Area
st.markdown("<h1 class='center-text'>🤖 PromptBridge AI Assistant</h1>", unsafe_allow_html=True)

# Display chat history
# check this out
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("<p class='center-text'>Start a conversation by sending a message</p>", unsafe_allow_html=True)
else:
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"<div class='user-message'>{message['content']}</div><div class='clearfix'></div>", unsafe_allow_html=True)
        else:
            response_time_html = ""
            if "response_time" in message:
                response_time_html = f"<span class='response-time'>⏱️ {message['response_time']}s</span>"
                
            st.markdown(f"<div class='assistant-message'>{message['content']}{response_time_html}</div><div class='clearfix'></div>", unsafe_allow_html=True)
            
            # Show keywords if available
            if "keywords" in message and message["keywords"]:
                keywords_str = ", ".join(message["keywords"])
                st.markdown(f"<div style='clear:both; font-size:0.8em; color: #a0aec0; margin-left:10px;'>🔑 Keywords: {keywords_str}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Create tabs for Text and Voice modes
if st.session_state.mode == "text":
    # Text input area
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Use the session state to store and retrieve the input value
        st.text_area(
            "Type your message",
            key="text_input",
            height=100,
            placeholder="Ask me anything in any language...",
            value=st.session_state.user_input,
            on_change=on_input_change
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        speak_response = st.checkbox("🔊 Speak response", key="speak_text_response")

        
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Send", key="send_button", use_container_width=True, on_click=on_send_button_click):
            st.rerun()
    
else:  # Voice Mode
    st.markdown("<div class='mode-selector'>", unsafe_allow_html=True)
    
    # Check recording status
    recording_active = check_recording_status()
    
    if recording_active:
        st.markdown("<p class='recording-active'>🔴 Recording in progress...</p>", unsafe_allow_html=True)
        
        # Show the ongoing status every 5 seconds (or your desired chunk duration)
        st.markdown("<p>🎤 Recording started. Speak now in chunks of 5 seconds!</p>", unsafe_allow_html=True)
        
        # Simulate the "transcribing" status
        st.markdown("<p>📡 Transcribing...</p>", unsafe_allow_html=True)
        
        # You can update or handle transcriptions here in real-time if possible
        # For example, after every 5-second chunk, you can update the transcription
        
    else:
        st.markdown("<p>Press Start to begin recording your voice</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎤 Start Recording", key="start_recording", use_container_width=True, disabled=recording_active):
            started = start_recording()
            if started:
                st.session_state.recording = True
                st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Recording", key="stop_recording", use_container_width=True, disabled=not recording_active):
            transcript = stop_recording_and_transcribe()
            if transcript:
                st.session_state.transcribed_input = transcript
                handle_user_input(transcript, True)  # Voice mode always speaks responses
                unload_whisper()
                st.session_state.recording = False
                st.rerun()
    
    # Show transcription if available
    if st.session_state.transcribed_input:
        st.markdown("<div class='status-info'>", unsafe_allow_html=True)
        st.markdown(f"📝 **Final Transcript:** {st.session_state.transcribed_input}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


# Footer with additional information
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #a0aec0; font-size: 0.8em;">
    Powered by advanced language models • Ask questions in any language
</div>
""", unsafe_allow_html=True)