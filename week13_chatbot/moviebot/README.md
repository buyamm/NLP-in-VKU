# 🎬 Movie Recommendation Chatbot

A conversational chatbot built with **Rasa Open Source 3.x** that recommends movies similar to one you like, powered by **TF-IDF** vectorization and **Cosine Similarity**.

---

## 📐 Architecture & Pipeline

```
User input
  │
  ▼
Rasa NLU
  ├─ Intent detection  → recommend_movie
  └─ Entity extraction → movie_title (e.g. "Inception")
  │
  ▼
Rasa Core (RulePolicy)
  └─ Triggers: action_recommend_movie
  │
  ▼
Custom Action Server (Rasa SDK)
  └─ actions/actions.py
       ├─ Read  data_movies/movies.csv  (pandas)
       ├─ Build TF-IDF matrix           (scikit-learn TfidfVectorizer)
       │    text = genres + description
       ├─ Compute cosine_similarity
       └─ Return top 3 similar movies
  │
  ▼
Bot response
  "🎬 Movies similar to Inception:
    1. Tenet        ████████░░  (similarity: 0.78)
    2. The Matrix   ███████░░░  (similarity: 0.74)
    3. Interstellar ██████░░░░  (similarity: 0.70)"
```

---

## 📁 Project Structure

```
moviebot/
├── actions/
│   ├── __init__.py
│   └── actions.py          ← TF-IDF recommendation logic
│
├── data/
│   ├── nlu.yml             ← Training examples (EN + VI)
│   └── rules.yml           ← Conversation rules
│
├── data_movies/
│   └── movies.csv          ← Movie dataset (16 movies)
│
├── models/                 ← Trained model output (auto-created)
│
├── config.yml              ← NLU pipeline + policies
├── credentials.yml         ← Channel credentials
├── domain.yml              ← Intents, entities, slots, responses
├── endpoints.yml           ← Action server endpoint
├── requirements.txt        ← Python dependencies
├── Dockerfile              ← Rasa server image
├── docker-compose.yml      ← Full stack orchestration
└── README.md
```

---

## 🚀 Quick Start (Docker — recommended)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 20.x
- [Docker Compose](https://docs.docker.com/compose/install/) ≥ 2.x

Verify installation:
```bash
docker --version
docker compose version
```

---

### Step 1 — Train the model

```bash
cd moviebot
docker compose --profile train run --rm trainer
```

This trains the Rasa NLU + Core model and saves it to `./models/moviebot.tar.gz`.

> ⏱ Training takes ~2–5 minutes on first run.

---

### Step 2 — Start the chatbot

```bash
docker compose up
```

This starts two services:
| Service | Container | Port |
|---|---|---|
| Rasa server | `moviebot_rasa` | `5005` |
| Action server | `moviebot_actions` | `5055` |

Wait until you see:
```
moviebot_rasa | Rasa server is up and running.
```

---

### Step 3 — Chat with the bot

#### Option A — REST API with curl (recommended)

```bash
# Say hello
curl -s -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "user1", "message": "hello"}' | python3 -m json.tool

# Get movie recommendations
curl -s -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "user1", "message": "recommend movie similar to Inception"}' | python3 -m json.tool

# Vietnamese
curl -s -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "user1", "message": "gợi ý phim giống Titanic"}' | python3 -m json.tool
```

#### Option B — Interactive shell via chat.sh (no extra port needed)

```bash
# Make executable (first time only)
chmod +x chat.sh

# Start chatting
./chat.sh
```

This script talks to the already-running Rasa server on port 5005 via REST —
no second server is started, no port conflict.

```
🎬  MovieBot Chat Shell
    Connecting to: http://localhost:5005/webhooks/rest/webhook
    Type 'quit' or Ctrl+C to exit
────────────────────────────────────

You: hello
Bot: Hi! I am MovieBot 🎬 Tell me a movie you like and I'll recommend similar ones!

You: recommend movie similar to Inception
Bot: 🎬 Movies similar to Inception:
       1. Tenet         ██░░░░░░░░  (similarity: 0.19)
       2. The Matrix    █░░░░░░░░░  (similarity: 0.13)
       3. Iron Man      █░░░░░░░░░  (similarity: 0.13)

You: quit
Bot: Goodbye! 🍿
```

> ⚠️ **Why NOT `rasa shell`?**
> `rasa shell` always starts a brand-new Rasa server internally.
> When the container already has a server on port 5005, it crashes with
> `[Errno 98] address already in use`.
> Use `./chat.sh` or curl instead.

---

## 💬 Example Conversations

```
You:  hello
Bot:  Hi! I am MovieBot 🎬 Tell me a movie you like and I'll recommend similar ones!

You:  recommend movie similar to Inception
Bot:  🎬 Movies similar to Inception:
        1. Tenet        ████████░░  (similarity: 0.78)
        2. The Matrix   ███████░░░  (similarity: 0.74)
        3. Interstellar ██████░░░░  (similarity: 0.70)

You:  gợi ý phim giống Titanic
Bot:  🎬 Movies similar to Titanic:
        1. The Notebook  ████████░░  (similarity: 0.82)
        2. La La Land    ██████░░░░  (similarity: 0.65)
        3. Coco          ████░░░░░░  (similarity: 0.41)

You:  find movies similar to John Wick
Bot:  🎬 Movies similar to John Wick:
        1. The Dark Knight  ███████░░░  (similarity: 0.72)
        2. Mad Max Fury Road ██████░░░░  (similarity: 0.68)
        3. Tenet            █████░░░░░  (similarity: 0.55)

You:  bye
Bot:  Goodbye! Enjoy your movies! 🍿
```

---

## ✨ Features

| Feature | Details |
|---|---|
| **Intent recognition** | `greet`, `goodbye`, `recommend_movie` |
| **Entity extraction** | `movie_title` via DIETClassifier |
| **Bilingual** | English + Vietnamese training examples |
| **TF-IDF vectorization** | `genres + description` combined text |
| **Cosine similarity** | scikit-learn `cosine_similarity` |
| **Fuzzy matching** | Handles typos: `intersteller` → `Interstellar` |
| **Similarity bar** | Visual `████░░░░░░` score display |
| **Model caching** | TF-IDF built once per container lifetime |
| **Full logging** | Timestamped logs at INFO level |
| **Exception handling** | Graceful errors for missing file / unknown movie |

---

## 🔧 Configuration

### Add more movies

Edit `data_movies/movies.csv`:
```csv
title,genres,description
Your Movie,"genre1 genre2","A short description of the movie."
```

### Retrain after changes

```bash
docker compose --profile train run --rm trainer
docker compose restart rasa
```

### Change number of recommendations

In `actions/actions.py`, find:
```python
if len(recommendations) == 3:
```
Change `3` to any number you want.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `Model not found` | Run the trainer step first |
| `Action server not reachable` | Check `endpoints.yml` URL matches service name |
| `Movie not found` | Check spelling; fuzzy matching handles minor typos |
| `Port already in use` | Change port mapping in `docker-compose.yml` |
| Slow first response | TF-IDF builds on first request; subsequent calls are cached |

### View logs

```bash
# All services
docker compose logs -f

# Rasa server only
docker compose logs -f rasa

# Action server only
docker compose logs -f action_server
```

### Stop everything

```bash
docker compose down
```

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| Chatbot framework | Rasa Open Source 3.6 |
| Action server | Rasa SDK 3.6 |
| NLU pipeline | DIETClassifier + CountVectorsFeaturizer |
| Recommendation | TF-IDF + Cosine Similarity |
| Data processing | pandas |
| ML library | scikit-learn |
| Containerization | Docker + Docker Compose |
| Language | Python 3.9+ |

---

## 📄 License

MIT — free to use and modify.
