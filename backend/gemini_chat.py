import os
import google.generativeai as genai

class GeminiChat:
    def __init__(self, model_name="models/gemini-1.5-flash-latest"):
        # Initializes Gemini API and starts a chat session
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment variables.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat = self.model.start_chat(history=[])
        print("✅ Gemini model initialized.")

    def send(self, message: str) -> str:
        # Sends a message to the Gemini model and returns the response
        response = self.chat.send_message(message)
        return response.text.strip()

    def reset_chat(self):
        # Resets the chat history
        self.chat = self.model.start_chat(history=[])

# === Function for use in main.py ===
gemini_instance = None

def get_gemini_response(prompt: str) -> str:
    # Returns the response from the Gemini model
    global gemini_instance
    if gemini_instance is None:
        gemini_instance = GeminiChat()
    return gemini_instance.send(prompt)

# === Optional CLI test ===
if __name__ == "__main__":
    gemini = GeminiChat()
    print("💬 Type 'exit' to stop chatting.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        reply = gemini.send(user_input)
        print("\nBot:", reply, "\n")


#Final copy