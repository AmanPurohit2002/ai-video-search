import os
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
import vecs
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

client_ai = genai.Client(api_key=GEMINI_API_KEY)
SUPABASE_DB_URL = os.environ.get("SUPABASE_DB_URL")
if not SUPABASE_DB_URL:
    raise ValueError("SUPABASE_DB_URL not found in .env file.")

vx = vecs.create_client(SUPABASE_DB_URL)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchQuery(BaseModel):
    query: str

@app.post("/search")
def search_videos(query_obj: SearchQuery):
    try:
        docs = vx.get_or_create_collection(name="ai_show_videos", dimension=3072)
    except Exception:
        raise HTTPException(status_code=500, detail="Supabase connection failed.")
    
    query = query_obj.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        # Embed the query
        response = client_ai.models.embed_content(
            model='gemini-embedding-2',
            contents=query,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
        )
        query_embedding = response.embeddings[0].values
        
        # Search Supabase pgvector using vecs
        results = docs.query(
            data=query_embedding,
            limit=5,
            include_value=True,
            include_metadata=True
        )
        
        output = []
        for doc_id, distance, meta in results:
            similarity = (1.0 - distance) * 100
            output.append({
                "id": doc_id,
                "title": meta.get('title', 'Unknown Title'),
                "summary": meta.get('summary', 'No summary available.'),
                "videoId": meta.get('videoId', ''),
                "seconds": meta.get('seconds', '0'),
                "start": meta.get('start', ''),
                "speaker": meta.get('speaker', 'Unknown'),
                "similarity": round(similarity, 1)
            })
                
        return {"results": output}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
