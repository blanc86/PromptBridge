import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Optional: Load BART model from Hugging Face on CPU only
try:
    from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
    import torch

    bart_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-base")
    bart_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-base").to("cpu")
    summarizer = pipeline("summarization", model=bart_model, tokenizer=bart_tokenizer, device=-1)
except ImportError:
    summarizer = None

# === SIMPLE SENTENCE SPLITTER ===

def split_sentences(text: str) -> list:
    return re.split(r'(?<=[.!?]) +', text.strip())

# === STOPWORD REMOVER (Optional Enhancement) ===

def remove_stopwords(text: str) -> str:
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    words = text.split()
    return ' '.join([word for word in words if word.lower() not in ENGLISH_STOP_WORDS])

# === KEYWORD HIGHLIGHTING (Optional Debug Tool) ===

def extract_keywords(text: str, top_k: int = 5) -> list:
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])
    indices = np.argsort(X.toarray()[0])[::-1]
    features = np.array(vectorizer.get_feature_names_out())
    return features[indices][:top_k].tolist()

# === SUMMARIZER (Aggressive Extractive or BART if available) ===

def summarize_text(text: str, num_sentences: int = 3) -> str:
    """
    Summarizes the text using BART if available; otherwise falls back to TF-IDF extractive method.
    """
    if summarizer:
        try:
            result = summarizer(text, max_length=120, min_length=60, do_sample=False)
            return result[0]['summary_text']
        except Exception:
            pass  # fallback in case BART fails

    # === FALLBACK: TF-IDF summarizer ===
    sentences = split_sentences(text)
    if len(sentences) <= num_sentences:
        return text

    tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_df=0.9)
    sentence_vectors = tfidf.fit_transform(sentences)
    sentence_scores = sentence_vectors.sum(axis=1).A1
    ranked_indices = np.argsort(sentence_scores)[::-1][:num_sentences]
    ranked_indices.sort()
    summary = ' '.join([sentences[i] for i in ranked_indices])
    return summary

# === CLEANER (Friendly Cleanup) ===

def friendly_clean(prompt: str) -> str:
    prompt = re.sub(r"\s{2,}", " ", prompt.strip())  # Remove extra spaces
    prompt = re.sub(r"\n+", " ", prompt)             # Replace newlines with spaces
    return prompt

# === TOOL INPUT OPTIMIZER ===

def optimize_tool_input(prompt: str) -> str:
    cleaned = friendly_clean(prompt)
    if len(cleaned) > 300:
        return summarize_text(cleaned, num_sentences=2)
    return cleaned

# === FOR IMPORT IN MAIN ===

def get_optimized_prompt_and_keywords(prompt: str):
    optimized = optimize_tool_input(prompt)
    keywords = extract_keywords(optimized)
    return optimized, keywords

# === EXAMPLE TEST ===

if __name__ == "__main__":
    sample_prompt = (
        """
        Artificial intelligence is a field of computer science that focuses on creating intelligent machines that work and react like humans. 
        Some of the activities computers with artificial intelligence are designed for include: speech recognition, learning, planning, and problem-solving. 
        As technology advances, artificial intelligence has become more integrated into daily life, from virtual assistants to recommendation algorithms. 
        AI also plays a crucial role in data analysis, helping businesses make data-driven decisions. 
        Despite its many benefits, AI raises ethical concerns such as job displacement, privacy, and biases in decision-making systems.
        """
    )

    print("\n--- Optimized Tool Input ---")
    optimized, keywords = get_optimized_prompt_and_keywords(sample_prompt)
    print(optimized)

    print("\n--- Extracted Keywords ---")
    print(keywords)
