import os
import json
import time
# pyrefly: ignore [missing-import]
import vecs
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_DB_URL = os.environ.get("SUPABASE_DB_URL")

if not GEMINI_API_KEY or not SUPABASE_DB_URL:
    raise ValueError("GEMINI_API_KEY and SUPABASE_DB_URL must be set in .env file.")

client_ai = genai.Client(api_key=GEMINI_API_KEY)
vx = vecs.create_client(SUPABASE_DB_URL)

EMBEDDING_MODEL = 'gemini-embedding-2'
collection_name = "ai_show_videos"

print("Connecting to Supabase and preparing collection...")
docs = vx.get_or_create_collection(name=collection_name, dimension=3072)

DATASET_FILE = "embedding_index_3m (1).json"
print(f"Loading dataset from {DATASET_FILE}...")
with open(DATASET_FILE, 'r', encoding='utf-8') as f:
    dataset = json.load(f)

print(f"Loaded {len(dataset)} records.")

def get_embedding(text):
    response = client_ai.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    return response.embeddings[0].values

print("Starting embedding generation and Supabase DB population...")
print("Note: This will take a while due to API rate limits.")

batch_size = 5
vectors = []

for i, record in enumerate(tqdm(dataset, desc="Processing Segments")):
    if 'ada_v2' in record:
        del record['ada_v2']
    
    title = record.get('title', '')
    summary = record.get('summary', '')
    text_to_embed = f"Title: {title}\nSummary: {summary}"
    
    try:
        emb = get_embedding(text_to_embed)
        meta = {k: str(v) for k, v in record.items()}
        vectors.append((f"video_{i}", emb, meta))
        
        if len(vectors) >= batch_size:
            docs.upsert(records=vectors)
            vectors = []
            time.sleep(4)  # basic rate limit handling

    except Exception as e:
        print(f"\nError on record {i}: {e}")
        time.sleep(10)

if len(vectors) > 0:
    docs.upsert(records=vectors)

print("\nCreating index for performance...")
docs.create_index()
vx.disconnect()

print("\nSuccessfully embedded and stored records in Supabase pgvector!")
