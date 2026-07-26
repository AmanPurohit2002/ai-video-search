# Semantic Search Application — AI Video Search

## Project Overview

A **semantic search application** that searches through **1,409 Microsoft AI Show YouTube video segments** using AI-powered similarity matching. Users enter natural language queries and receive the Top-5 most relevant video segments with timestamped YouTube links.

## Problem Statement

An EdTech startup has a large collection of Microsoft AI Show YouTube videos. Students struggle to find specific topics across hundreds of videos. This application solves that by enabling semantic search over pre-chunked video transcripts using cosine similarity on embeddings.

## How to Run

1. **Start the FastAPI Backend** (in one terminal):
   ```bash
   .\venv\Scripts\uvicorn main:app --app-dir backend --port 8000
   ```
2. **Start the React Frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.
3. **Type a query** — e.g., *"What are Jupyter Notebooks?"*
4. **Click Search** or press **Enter**.
5. View the **Top-5 results** with video titles, summaries, scores, and clickable YouTube links.

> **No server required** — the app runs entirely in the browser.

## Search Modes

### Text Search (Default — No API Key Needed)
- Uses **TF-IDF** (Term Frequency–Inverse Document Frequency) vectorization on document summaries.
- Computes **cosine similarity** between the query's TF-IDF vector and each document's TF-IDF vector.
- Fast, works offline, no API credentials required.

### Embedding Search (Requires Free Google Gemini API Key)
- Sends the query to the **Google Gemini Embedding API** (`text-embedding-004`) to generate a query embedding.
- Computes **cosine similarity** between the query embedding and each document's pre-computed **OpenAI ada_v2** embedding (1536 dimensions).
- Demonstrates the full end-to-end embedding search pipeline.
- Get a free API key at: https://aistudio.google.com/apikey

> **Note:** Since the query embeddings (Gemini) and document embeddings (OpenAI ada_v2) come from different models, the semantic matching is approximate. This is expected and acceptable per the project guidelines.

## Technical Architecture

```
┌─────────────────────────────────────────────┐
│                  Browser                     │
│                                              │
│  ┌─────────┐    ┌──────────────────────┐     │
│  │  User    │───▶│   Search Engine      │     │
│  │  Query   │    │                      │     │
│  └─────────┘    │  Mode A: TF-IDF      │     │
│                 │  - Tokenize query     │     │
│                 │  - Compute TF-IDF vec │     │
│                 │  - Cosine similarity  │     │
│                 │                      │     │
│                 │  Mode B: Embedding    │     │
│                 │  - Gemini API embed   │     │
│                 │  - Cosine similarity  │     │
│                 │    vs ada_v2 vectors  │     │
│                 └──────────┬───────────┘     │
│                            │                 │
│                 ┌──────────▼───────────┐     │
│                 │  Rank & Display      │     │
│                 │  Top-5 Results       │     │
│                 │  - Title, Summary    │     │
│                 │  - Score, Timestamp  │     │
│                 │  - YouTube Link      │     │
│                 └──────────────────────┘     │
└─────────────────────────────────────────────┘
```

## Key Algorithms

### Cosine Similarity
```
cos(A, B) = (A · B) / (||A|| × ||B||)
```
Where `A · B` is the dot product and `||A||` is the L2 norm. Returns a value between -1 and 1, where 1 means identical direction.

### TF-IDF
- **TF** (Term Frequency): How often a word appears in a document, normalized by max frequency.
- **IDF** (Inverse Document Frequency): `log(N / df) + 1`, where N is total documents and df is document frequency.
- The product TF × IDF gives higher weight to words that are distinctive to a document.

## Dataset

- **File:** `embedding_index_3m (1).json`
- **Records:** 1,409 video segments (3-minute chunks)
- **Fields:** speaker, title, videoId, start, seconds, summary, ada_v2 (1536-dim embedding)

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | HTML5 + CSS3 + Vanilla JavaScript |
| Embedding API | Google Gemini (text-embedding-004) |
| Search | Cosine Similarity, TF-IDF |
| Design | Dark mode, Glassmorphism, CSS animations |

## Files

| File | Description |
|------|-------------|
| `index.html` | Main application page |
| `style.css` | Premium dark-mode styling |
| `app.js` | Search engine & UI logic |
| `README.md` | Project documentation |
| `embedding_index_3m (1).json` | Dataset with embeddings |
