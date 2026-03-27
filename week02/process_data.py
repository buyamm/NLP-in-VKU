import json
import os
import spacy
from langdetect import detect
from collections import Counter
from nltk.stem import PorterStemmer
from spellchecker import SpellChecker

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize tools
stemmer = PorterStemmer()
spell = SpellChecker(language="en")

# Load data
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Create output folder
os.makedirs("output", exist_ok=True)

# Containers
lang_results = []
sentence_results = []
normalized_results = []
tokens_results = []
tokens_no_stop_results = []
stem_lemma_results = []

all_tokens_no_stop = []

for article in data:
    for comment in article["comments"]:
        text = comment["content"]

# ================= 1. Language Detection ==================
        try:
            lang = detect(text)
        except:
            lang = "unknown"

        lang_results.append({
            "comment": text,
            "language": lang
        })

        if lang != "en":
            continue

        doc = nlp(text)

# ================= 2. Sentence Segmentation =================
        sentences = [sent.text for sent in doc.sents]
        sentence_results.append({
            "comment": text,
            "sentences": sentences
        })

# ================= 3. Text Normalization =================
        for sent in sentences:
            sent_doc = nlp(sent)

            normalized_tokens = [
                token.lower_
                for token in sent_doc
                if not token.is_punct and not token.is_space
            ]

            normalized_results.append({
                "sentence": sent,
                "normalized_text": " ".join(normalized_tokens)
            })

# ================= 4. Tokenization =================
            tokens = [token.text for token in sent_doc if token.is_alpha]
            tokens_results.append({
                "sentence": sent,
                "tokens": tokens
            })

# ================= 5. Stopword =================
            tokens_no_stop = [
                token.lower_
                for token in sent_doc
                if token.is_alpha and not token.is_stop
            ]

            tokens_no_stop_results.append({
                "sentence": sent,
                "tokens_no_stopwords": tokens_no_stop
            })

            all_tokens_no_stop.extend(tokens_no_stop)

# ================= 7. Stemming & Lemmatization + Spell Checking =================
            for token in sent_doc:
                if token.is_alpha and not token.is_stop:
                    normalized = token.lower_

                    corrected = spell.correction(normalized)
                    corrected = corrected if corrected else normalized

                    stem_lemma_results.append({
                        "original": token.text,
                        "corrected": corrected,
                        "stem": stemmer.stem(corrected),
                        "lemma": token.lemma_.lower()
                    })

# 6. Word Frequency Statistics
word_freq = Counter(all_tokens_no_stop)

# ===== SAVE RESULTS =====
with open("output/01_language_detection.json", "w", encoding="utf-8") as f:
    json.dump(lang_results, f, ensure_ascii=False, indent=2)

with open("output/02_sentence_segmentation.json", "w", encoding="utf-8") as f:
    json.dump(sentence_results, f, ensure_ascii=False, indent=2)

with open("output/03_normalized_text.json", "w", encoding="utf-8") as f:
    json.dump(normalized_results, f, ensure_ascii=False, indent=2)

with open("output/04_tokens.json", "w", encoding="utf-8") as f:
    json.dump(tokens_results, f, ensure_ascii=False, indent=2)

with open("output/05_tokens_no_stopwords.json", "w", encoding="utf-8") as f:
    json.dump(tokens_no_stop_results, f, ensure_ascii=False, indent=2)

with open("output/06_word_frequency.json", "w", encoding="utf-8") as f:
    json.dump(word_freq.most_common(), f, ensure_ascii=False, indent=2)

with open("output/07_stemming_vs_lemmatization.json", "w", encoding="utf-8") as f:
    json.dump(stem_lemma_results, f, ensure_ascii=False, indent=2)
