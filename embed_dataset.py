import os
import json
import time
# pyrefly: ignore [missing-import]
import chromadb
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not found. Please add it to your .env file.")

# Initialize the new google-genai client
client_ai = genai.Client(api_key=GEMINI_API_KEY)

EMBEDDING_MODEL = 'gemini-embedding-2'
CHROMA_DATA_PATH = "chroma_db"

client_chroma = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
collection_name = "ai_show_videos"

try:
    client_chroma.delete_collection(name=collection_name)
except Exception:
    pass

collection = client_chroma.create_collection(
    name=collection_name, 
    metadata={"hnsw:space": "cosine"}
)

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

print("Starting embedding generation and DB population...")
print("Note: This will take a while due to API rate limits.")

batch_size = 5
docs = []
metadatas = []
ids = []
embeddings = []

for i, record in enumerate(tqdm(dataset, desc="Processing Segments")):
    if 'ada_v2' in record:
        del record['ada_v2']
    
    title = record.get('title', '')
    summary = record.get('summary', '')
    text_to_embed = f"Title: {title}\nSummary: {summary}"
    
    try:
        emb = get_embedding(text_to_embed)
        
        docs.append(text_to_embed)
        meta = {k: str(v) for k, v in record.items()}
        metadatas.append(meta)
        ids.append(f"video_{i}")
        embeddings.append(emb)
        
        if len(ids) >= batch_size:
            collection.add(
                documents=docs,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            docs, metadatas, ids, embeddings = [], [], [], []
            time.sleep(4)  # basic rate limit handling

    except Exception as e:
        print(f"\nError on record {i}: {e}")
        time.sleep(10)

if len(ids) > 0:
    collection.add(
        documents=docs,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

print(f"\nSuccessfully embedded and stored records in ChromaDB at ./{CHROMA_DATA_PATH}")
