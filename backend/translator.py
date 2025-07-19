from transformers import NllbTokenizer, AutoModelForSeq2SeqLM
import torch
from langdetect import detect

class NLLBTranslator:
    def __init__(self, model_name="facebook/nllb-200-distilled-600M"):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        print(f"🧠 Translator ready. Model will load lazily on first use.")

        self.lang_code_to_id = None
        self.lang_detect_map = {
            "as": "asm_Beng",
            "bn": "ben_Beng",
            "brx": "npi_Deva",
            "doi": "hin_Deva",
            "en": "eng_Latn",
            "gom": "mar_Deva",
            "gu": "guj_Gujr",
            "hi": "hin_Deva",
            "kn": "kan_Knda",
            "ks": "urd_Arab",
            "mai": "hin_Deva",
            "ml": "mal_Mlym",
            "mr": "mar_Deva",
            "ne": "npi_Deva",
            "pa": "pan_Guru",
            "sa": "san_Deva",
            "sd": "snd_Arab",
            "ta": "tam_Taml",
            "te": "tel_Telu",
            "ur": "urd_Arab"
        }

    def _load_model(self):
        if self.model is None or self.tokenizer is None:
            print(f"🚀 Loading NLLB model to {self.device}...")
            self.tokenizer = NllbTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self.device)
            self.lang_code_to_id = self.tokenizer.convert_tokens_to_ids
            print("✅ NLLB Model and Tokenizer loaded.")

    def detect_lang_code(self, text):
        lang = detect(text)
        return lang  # Return ISO 639-1 code like "hi", "bn", etc.

    def translate_to_english(self, text):
        self._load_model()
        iso_code = self.detect_lang_code(text)
        source_lang = self.lang_detect_map.get(iso_code, "eng_Latn")
        print(f"🌐 Translating from {source_lang} → eng_Latn...")
        print(f"🔤 Input text: {text}")
        return self._translate(text, source_lang, "eng_Latn")

    def translate_from_english(self, text, target_lang_code):
        self._load_model()

        target_lang = self.lang_detect_map.get(target_lang_code)
        if not target_lang:
            raise ValueError(f"❌ Unsupported or unknown target language code: {target_lang_code}")

        print(f"🌐 Translating from eng_Latn → {target_lang}...")
        print(f"🔤 Input text: {text}")
        return self._translate(text, "eng_Latn", target_lang)

    def _translate(self, text, source_lang, target_lang):
        self.tokenizer.src_lang = source_lang
        encoded = self.tokenizer(text, return_tensors="pt").to(self.device)

        target_lang_id = self.lang_code_to_id(target_lang)
        if target_lang_id is None:
            raise ValueError(f"❌ Invalid target language code: {target_lang}")

        generated_tokens = self.model.generate(
            **encoded,
            forced_bos_token_id=target_lang_id,
            max_length=256
        )

        translated = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        print(f"📝 Translated text: {translated}")
        return translated

    def unload(self):
        print("🧹 Unloading NLLB model from memory...")
        del self.model
        del self.tokenizer
        self.model = None
        self.tokenizer = None
        torch.cuda.empty_cache()
        print("✅ Translator unloaded successfully.")

# === Shared instance ===
translator_instance = NLLBTranslator()

# === External utility functions ===
def get_translated_text(text):
    return translator_instance.translate_to_english(text)

def translate_to_user_lang(text, target_lang_code):
    return translator_instance.translate_from_english(text, target_lang_code)

def unload_translator():
    translator_instance.unload()

def get_translator_instance():
    return translator_instance


# === For testing ===
if __name__ == "__main__":
    test_cases = {
        "as": "আপুনাৰ নাম কি?",
        "bn": "তোমার নাম কী?",
        "brx": "नङाइ जोनाय हो?",
        "doi": "तूहाडा नाँव की ऐ?",
        "en": "What is your name?",
        "gom": "तुझे नाव किते?",
        "gu": "તમારું નામ શું છે?",
        "hi": "तुम्हारा नाम क्या है?",
        "kn": "ನಿಮ್ಮ ಹೆಸರೇನು?",
        "ks": "تُهند ناو کٔیہ چھُ?",
        "mai": "अहाँक नाम की अछि?",
        "ml": "നിന്റെ പേര് എന്താണ്?",
        "mr": "तुझे नाव काय आहे?",
        "ne": "तिम्रो नाम के हो?",
        "pa": "ਤੁਹਾਡਾ ਨਾਂ ਕੀ ਹੈ?",
        "sa": "तव नाम किम् अस्ति?",
        "sd": "توھانجو نالو ڇا آهي؟",
        "ta": "உங்கள் பெயர் என்ன?",
        "te": "మీ పేరు ఏమిటి?",
        "ur": "آپ کا نام کیا ہے؟"
    }

    for lang, input_text in test_cases.items():
        print(f"\n🔎 Testing for language code: {lang}")
        try:
            translated = translator_instance.translate_to_english(input_text)
            back_translated = translator_instance.translate_from_english(translated, lang)
            print(f"🔁 Round-trip: {back_translated}")
        except Exception as e:
            print(f"❌ Error: {e}")

    translator_instance.unload()
