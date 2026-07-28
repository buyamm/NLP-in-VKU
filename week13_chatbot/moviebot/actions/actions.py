"""
Movie Recommendation Action for Rasa Chatbot.

Pipeline:
  User input
    → Rasa NLU detects intent: recommend_movie
    → Extracts entity: movie_title
    → Calls ActionRecommendMovie.run()
    → Reads data_movies/movies.csv
    → Builds TF-IDF matrix on genres + description
    → Computes cosine similarity
    → Returns top 3 most similar movies
"""

import os
import logging
from typing import Any, Text, Dict, List

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dataset path — works both locally and inside Docker container
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data_movies", "movies.csv")

# ---------------------------------------------------------------------------
# Module-level cache so TF-IDF is only built once per container lifetime
# ---------------------------------------------------------------------------
_cache: Dict[str, Any] = {
    "df": None,
    "tfidf_matrix": None,
    "vectorizer": None,
    "titles_lower": None,
}


def _load_and_build_model() -> bool:
    if _cache["df"] is not None:
        logger.info("TF-IDF model already cached — skipping rebuild.")
        return True

    if not os.path.exists(DATASET_PATH):
        logger.error("Dataset not found at: %s", DATASET_PATH)
        return False

    try:
        logger.info("Loading dataset from: %s", DATASET_PATH)
        df = pd.read_csv(DATASET_PATH)

        # Validate required columns
        required_cols = {"title", "genres", "description"}
        missing = required_cols - set(df.columns)
        if missing:
            logger.error("Missing columns in CSV: %s", missing)
            return False

        # Fill NaN values to avoid vectorizer errors
        df["genres"] = df["genres"].fillna("")
        df["description"] = df["description"].fillna("")

        # Combine genres + description into a single text feature
        df["text"] = df["genres"] + " " + df["description"]

        # Build TF-IDF matrix
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(df["text"])

        # Pre-compute lowercase titles for fuzzy matching
        titles_lower = df["title"].str.lower().tolist()

        # Store in cache
        _cache["df"] = df
        _cache["tfidf_matrix"] = tfidf_matrix
        _cache["vectorizer"] = vectorizer
        _cache["titles_lower"] = titles_lower

        logger.info(
            "TF-IDF model built successfully. %d movies loaded.", len(df)
        )
        return True

    except Exception as exc:
        logger.exception("Failed to build TF-IDF model: %s", exc)
        return False


def _char_similarity(a: str, b: str) -> float:
    """
    Simple character-level Jaccard similarity between two strings.
    Uses bigrams (pairs of consecutive characters).
    Useful for catching typos like 'intersteller' vs 'interstellar'.
    """
    def bigrams(s: str):
        return set(s[i : i + 2] for i in range(len(s) - 1))

    bg_a = bigrams(a)
    bg_b = bigrams(b)
    if not bg_a or not bg_b:
        return 0.0
    intersection = len(bg_a & bg_b)
    union = len(bg_a | bg_b)
    return intersection / union if union else 0.0


def _fuzzy_find_title(query: str, titles_lower: List[str]) -> int:
    """
    Find the best matching movie index using a multi-strategy approach:
      1. Exact match (case-insensitive)
      2. Substring match (query inside title or title inside query)
      3. Token overlap (handles partial names)
      4. Character bigram similarity (handles typos like 'intersteller')

    Returns:
        Index of the best match, or -1 if nothing found.
    """
    query_clean = query.lower().strip()

    # Strategy 1: exact match
    if query_clean in titles_lower:
        return titles_lower.index(query_clean)

    # Strategy 2: substring match
    for idx, title in enumerate(titles_lower):
        if query_clean in title or title in query_clean:
            return idx

    # Strategy 3: token overlap
    query_tokens = set(query_clean.split())
    best_idx = -1
    best_overlap = 0

    for idx, title in enumerate(titles_lower):
        title_tokens = set(title.split())
        overlap = len(query_tokens & title_tokens)
        if overlap > best_overlap:
            best_overlap = overlap
            best_idx = idx

    if best_overlap >= 1:
        return best_idx

    # Strategy 4: character bigram similarity (typo tolerance)
    # Also try matching each word in the query against each title word
    best_char_idx = -1
    best_char_score = 0.0
    CHAR_THRESHOLD = 0.5  # require at least 50% bigram overlap

    for idx, title in enumerate(titles_lower):
        # Compare full strings
        score = _char_similarity(query_clean, title)
        # Also compare each query word against each title word
        for q_word in query_clean.split():
            for t_word in title.split():
                word_score = _char_similarity(q_word, t_word)
                if word_score > score:
                    score = word_score
        if score > best_char_score:
            best_char_score = score
            best_char_idx = idx

    if best_char_score >= CHAR_THRESHOLD:
        logger.info(
            "Fuzzy (bigram) match: '%s' → '%s' (score %.2f)",
            query_clean,
            titles_lower[best_char_idx],
            best_char_score,
        )
        return best_char_idx

    return -1


class ActionRecommendMovie(Action):
    """
    Custom Rasa action that recommends movies similar to the one
    provided by the user, using TF-IDF + cosine similarity.
    """

    def name(self) -> Text:
        return "action_recommend_movie"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # ------------------------------------------------------------------
        # 1. Get the movie title from the slot
        # ------------------------------------------------------------------
        movie_title: str = tracker.get_slot("movie_title")
        logger.info("Received movie_title slot: '%s'", movie_title)

        if not movie_title or not movie_title.strip():
            dispatcher.utter_message(
                text="Please tell me a movie title first. "
                     "For example: 'recommend movies similar to Inception'"
            )
            return []

        movie_title = movie_title.strip()

        # ------------------------------------------------------------------
        # 2. Load dataset and build TF-IDF model (cached after first call)
        # ------------------------------------------------------------------
        if not _load_and_build_model():
            dispatcher.utter_message(
                text="⚠️ Movie dataset not found. "
                     "Please make sure 'data_movies/movies.csv' exists."
            )
            return []

        df: pd.DataFrame = _cache["df"]
        tfidf_matrix = _cache["tfidf_matrix"]
        titles_lower: List[str] = _cache["titles_lower"]

        # ------------------------------------------------------------------
        # 3. Find the movie in the dataset (fuzzy matching)
        # ------------------------------------------------------------------
        movie_idx = _fuzzy_find_title(movie_title, titles_lower)

        if movie_idx == -1:
            logger.warning("Movie not found: '%s'", movie_title)
            dispatcher.utter_message(
                text=(
                    f"Sorry, I cannot find '{movie_title}' in the movie dataset. 😕\n"
                    "Try one of these: Inception, Interstellar, The Matrix, "
                    "Titanic, Toy Story, John Wick, Avatar, The Dark Knight."
                )
            )
            return [SlotSet("movie_title", None)]

        matched_title: str = df.iloc[movie_idx]["title"]
        logger.info(
            "Matched '%s' → '%s' (index %d)", movie_title, matched_title, movie_idx
        )

        # ------------------------------------------------------------------
        # 4. Compute cosine similarity
        # ------------------------------------------------------------------
        try:
            movie_vector = tfidf_matrix[movie_idx]
            similarity_scores = cosine_similarity(movie_vector, tfidf_matrix).flatten()
        except Exception as exc:
            logger.exception("Error computing cosine similarity: %s", exc)
            dispatcher.utter_message(
                text="An error occurred while computing recommendations. Please try again."
            )
            return []

        # ------------------------------------------------------------------
        # 5. Get top 3 similar movies (excluding the movie itself)
        # ------------------------------------------------------------------
        # argsort ascending → reverse for descending
        sorted_indices = similarity_scores.argsort()[::-1]

        recommendations = []
        for idx in sorted_indices:
            if idx == movie_idx:
                continue  # skip the movie itself
            score = similarity_scores[idx]
            title = df.iloc[idx]["title"]
            recommendations.append((title, score))
            if len(recommendations) == 3:
                break

        # ------------------------------------------------------------------
        # 6. Build and send the response message
        # ------------------------------------------------------------------
        if not recommendations:
            dispatcher.utter_message(
                text=f"I couldn't find any movies similar to '{matched_title}'. 😔"
            )
            return [SlotSet("movie_title", None)]

        lines = [f"🎬 Movies similar to **{matched_title}**:\n"]
        for rank, (title, score) in enumerate(recommendations, start=1):
            bar = _score_bar(score)
            lines.append(f"  {rank}. {title}  {bar}  (similarity: {score:.2f})")

        response_text = "\n".join(lines)
        logger.info("Sending recommendations:\n%s", response_text)
        dispatcher.utter_message(text=response_text)

        # Reset slot so the user can ask again cleanly
        return [SlotSet("movie_title", None)]


def _score_bar(score: float) -> str:
    """
    Convert a similarity score (0.0 – 1.0) to a small visual bar.
    Example: 0.75 → '████░░░░░░'
    """
    filled = int(round(score * 10))
    empty = 10 - filled
    return "█" * filled + "░" * empty
