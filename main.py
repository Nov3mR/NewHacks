from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from datetime import datetime
from dotenv import load_dotenv
import json
import uuid

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI first
app = FastAPI(title="Travel Buddy RAG API")

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Next.js URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and configure Gemini
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model_names = ['gemini-2.0-flash']
        gemini_model = None
        for model_name in model_names:
            try:
                gemini_model = genai.GenerativeModel(model_name)
                print(f"✅ Gemini configured successfully with model: {model_name}")
                break
            except Exception:
                continue
        if gemini_model is None:
            print("❌ No available Gemini models found")
    else:
        print("⚠️  WARNING: GEMINI_API_KEY not set!")
        gemini_model = None
except Exception as e:
    print(f"❌ Error configuring Gemini: {e}")
    gemini_model = None

# Import other dependencies
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    import PyPDF2
    import io
    
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Embedding model loaded successfully")
except Exception as e:
    print(f"❌ Error loading dependencies: {e}")
    embedding_model = None

# Storage directories
STORAGE_DIR = "storage"
USERS_DIR = os.path.join(STORAGE_DIR, "users")
TRAVEL_DATA_DIR = os.path.join(STORAGE_DIR, "travel_data")
VECTOR_STORE_FILE = os.path.join(STORAGE_DIR, "vector_store.json")
DATA_DIR = "data"  # Folder where you put your travel documents

# Create storage directories
os.makedirs(USERS_DIR, exist_ok=True)
os.makedirs(TRAVEL_DATA_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Vector Store with persistence
class VectorStore:
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.metadata = []
        self.load_from_disk()
    
    def add_documents(self, texts: List[str], metadata: List[dict]):
        if embedding_model is None:
            raise Exception("Embedding model not loaded")
        embeddings = embedding_model.encode(texts)
        self.documents.extend(texts)
        self.embeddings.extend(embeddings.tolist())
        self.metadata.extend(metadata)
        self.save_to_disk()
    
    def search(self, query: str, top_k: int = 5, filter_type: str = None):
        if not self.embeddings:
            return []
        if embedding_model is None:
            raise Exception("Embedding model not loaded")
        
        query_embedding = embedding_model.encode([query])
        embeddings_array = np.array(self.embeddings)
        similarities = cosine_similarity(query_embedding, embeddings_array)[0]
        
        # Filter by type if specified
        if filter_type:
            filtered_indices = [i for i, meta in enumerate(self.metadata) if meta.get("type") == filter_type]
        else:
            filtered_indices = list(range(len(similarities)))
        
        # Get top k from filtered results
        filtered_similarities = [(i, similarities[i]) for i in filtered_indices]
        filtered_similarities.sort(key=lambda x: x[1], reverse=True)
        top_indices = [i for i, _ in filtered_similarities[:top_k]]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                results.append({
                    "text": self.documents[idx],
                    "score": float(similarities[idx]),
                    "metadata": self.metadata[idx]
                })
        return results
    
    def save_to_disk(self):
        try:
            data = {
                "documents": self.documents,
                "embeddings": self.embeddings,
                "metadata": self.metadata
            }
            with open(VECTOR_STORE_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving vector store: {e}")
    
    def load_from_disk(self):
        try:
            if os.path.exists(VECTOR_STORE_FILE):
                with open(VECTOR_STORE_FILE, 'r') as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.embeddings = data.get("embeddings", [])
                    self.metadata = data.get("metadata", [])
                print(f"✅ Loaded {len(self.documents)} documents from disk")
        except Exception as e:
            print(f"Error loading vector store: {e}")

vector_store = VectorStore()

# User Profile Storage
class UserProfileStore:
    @staticmethod
    def get_or_create_profile(user_id: str):
        profile_file = os.path.join(USERS_DIR, f"{user_id}.json")
        try:
            if os.path.exists(profile_file):
                with open(profile_file, 'r') as f:
                    return json.load(f)
            else:
                profile = {
                    "user_id": user_id,
                    "visited_countries": [],
                    "preferences": {},
                    "travel_history": [],
                    "created_at": datetime.now().isoformat()
                }
                with open(profile_file, 'w') as f:
                    json.dump(profile, f, indent=2)
                return profile
        except Exception as e:
            print(f"Error with user profile: {e}")
            return None
    
    @staticmethod
    def update_profile(user_id: str, updates: dict):
        profile_file = os.path.join(USERS_DIR, f"{user_id}.json")
        try:
            profile = UserProfileStore.get_or_create_profile(user_id)
            if profile:
                profile.update(updates)
                profile["updated_at"] = datetime.now().isoformat()
                with open(profile_file, 'w') as f:
                    json.dump(profile, f, indent=2)
                return profile
        except Exception as e:
            print(f"Error updating profile: {e}")
        return None
    
    @staticmethod
    def add_visited_country(user_id: str, country: str, visit_date: str = None):
        profile = UserProfileStore.get_or_create_profile(user_id)
        if profile:
            if country not in profile["visited_countries"]:
                profile["visited_countries"].append(country)
            profile["travel_history"].append({
                "country": country,
                "visit_date": visit_date or datetime.now().isoformat()
            })
            return UserProfileStore.update_profile(user_id, profile)
        return None

# Pydantic models
class ActivityRequest(BaseModel):
    user_id: str
    country: str
    interests: Optional[List[str]] = []
    duration_days: Optional[int] = None

class CountryRecommendationRequest(BaseModel):
    user_id: str
    budget: Optional[str] = None  # "budget", "moderate", "luxury"
    travel_style: Optional[str] = None  # "adventure", "relaxation", "cultural", "foodie"

class TranslationRequest(BaseModel):
    text: str
    target_language: str
    context: Optional[str] = None

class TravelResponse(BaseModel):
    response: str
    recommendations: List[dict]
    sources: Optional[List[dict]] = []

class UserProfileUpdate(BaseModel):
    visited_countries: Optional[List[str]] = None
    preferences: Optional[dict] = None

# Helper function for Gemini
def generate_gemini_response(prompt: str) -> str:
    if gemini_model is None:
        raise HTTPException(status_code=500, detail="Gemini model not configured")
    response = gemini_model.generate_content(prompt)
    return response.text

# API Endpoints
@app.get("/")
def root():
    return {
        "message": "Travel Buddy RAG API",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "Activity recommendations based on country and interests",
            "Country recommendations based on travel history",
            "Translation to local languages with travel context"
        ],
        "endpoints": {
            "/api/activities": "POST - Get activity recommendations for a country",
            "/api/recommend-countries": "POST - Get country recommendations",
            "/api/translate": "POST - Translate text to target language",
            "/api/users/{user_id}": "GET - Get user profile",
            "/api/users/{user_id}": "PUT - Update user profile",
            "/api/users/{user_id}/visited": "POST - Add visited country"
        }
    }

@app.post("/api/activities", response_model=TravelResponse)
async def get_activities(request: ActivityRequest):
    """Get activity recommendations for a specific country"""
    try:
        # Get user profile for personalization
        profile = UserProfileStore.get_or_create_profile(request.user_id)
        
        # Search for relevant travel information
        query = f"activities things to do {request.country} {' '.join(request.interests)}"
        relevant_docs = vector_store.search(query, top_k=5, filter_type="activity")
        
        # Build context from RAG
        rag_context = ""
        if relevant_docs:
            rag_context = "\n\nRelevant Travel Information:\n"
            rag_context += "\n".join([doc["text"] for doc in relevant_docs])
        
        # Build prompt
        interests_str = ", ".join(request.interests) if request.interests else "general sightseeing"
        duration_str = f" for {request.duration_days} days" if request.duration_days else ""
        
        prompt = f"""You are a knowledgeable travel advisor specializing in {request.country}.

User Profile:
- Previously visited: {', '.join(profile.get('visited_countries', [])) if profile.get('visited_countries') else 'No previous travels'}
- Interests: {interests_str}
- Duration: {duration_str}

{rag_context}

Task: Provide 5-7 specific, actionable activity recommendations for {request.country} tailored to the user's interests.

Format your response as a JSON array with this structure:
[
  {{
    "name": "Activity name",
    "description": "Brief description (2-3 sentences)",
    "category": "category (adventure/cultural/food/nature/etc)",
    "location": "specific location or region",
    "estimated_cost": "budget estimate ($ / $$ / $$$)",
    "best_time": "best time to visit/do this",
    "tips": "insider tip or important note"
  }}
]

Only return the JSON array, no additional text."""

        response_text = generate_gemini_response(prompt)
        
        # Parse JSON from response
        try:
            # Clean the response to extract JSON
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                recommendations = json.loads(json_str)
            else:
                recommendations = []
        except:
            recommendations = []
        
        return TravelResponse(
            response=response_text,
            recommendations=recommendations,
            sources=relevant_docs
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend-countries", response_model=TravelResponse)
async def recommend_countries(request: CountryRecommendationRequest):
    """Recommend countries based on user's travel history and preferences"""
    try:
        # Get user profile
        profile = UserProfileStore.get_or_create_profile(request.user_id)
        visited = profile.get('visited_countries', [])
        
        # Search for similar destinations
        query = f"travel destinations similar to {' '.join(visited)} {request.travel_style or ''}"
        relevant_docs = vector_store.search(query, top_k=5, filter_type="destination")
        
        # Build context
        rag_context = ""
        if relevant_docs:
            rag_context = "\n\nRelevant Travel Information:\n"
            rag_context += "\n".join([doc["text"] for doc in relevant_docs])
        
        visited_str = ", ".join(visited) if visited else "None yet - this is their first trip!"
        
        prompt = f"""You are an expert travel advisor helping users discover their next destination.

User's Travel Profile:
- Countries visited: {visited_str}
- Budget preference: {request.budget or 'moderate'}
- Travel style: {request.travel_style or 'mixed interests'}

{rag_context}

Task: Recommend 5 countries the user should visit next, considering:
1. Similar vibes to places they've enjoyed (if any)
2. Natural progression in their travel journey
3. Their budget and travel style
4. Diverse experiences

Format as JSON array:
[
  {{
    "country": "Country name",
    "reason": "Why this matches their profile (2-3 sentences)",
    "highlights": ["highlight 1", "highlight 2", "highlight 3"],
    "best_for": "What type of traveler this is perfect for",
    "estimated_budget": "budget range per day",
    "best_season": "best time to visit",
    "similar_to": "which of their visited countries it resembles (if applicable)"
  }}
]

Only return the JSON array."""

        response_text = generate_gemini_response(prompt)
        
        # Parse JSON
        try:
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                recommendations = json.loads(json_str)
            else:
                recommendations = []
        except:
            recommendations = []
        
        return TravelResponse(
            response=response_text,
            recommendations=recommendations,
            sources=relevant_docs
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate")
async def translate_text(request: TranslationRequest):
    """Translate text to target language with travel context"""
    try:
        context_note = ""
        if request.context:
            context_note = f"\nContext: {request.context} (e.g., ordering food, asking directions, etc.)"
        
        prompt = f"""You are a helpful travel translator. Translate the following text to {request.target_language}.
{context_note}

Text to translate: "{request.text}"

Provide:
1. The translation
2. Pronunciation guide (phonetic)
3. Cultural note or usage tip (1 sentence)

Format as JSON:
{{
  "translation": "translated text",
  "pronunciation": "phonetic pronunciation",
  "cultural_note": "helpful context",
  "formality": "formal/casual"
}}

Only return the JSON object."""

        response_text = generate_gemini_response(prompt)
        
        # Parse JSON
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                translation_data = json.loads(json_str)
            else:
                translation_data = {
                    "translation": response_text,
                    "pronunciation": "",
                    "cultural_note": "",
                    "formality": "neutral"
                }
        except:
            translation_data = {
                "translation": response_text,
                "pronunciation": "",
                "cultural_note": "",
                "formality": "neutral"
            }
        
        return translation_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}")
def get_user_profile(user_id: str):
    """Get user profile"""
    try:
        profile = UserProfileStore.get_or_create_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/users/{user_id}")
def update_user_profile(user_id: str, updates: UserProfileUpdate):
    """Update user profile"""
    try:
        update_dict = {}
        if updates.visited_countries is not None:
            update_dict["visited_countries"] = updates.visited_countries
        if updates.preferences is not None:
            update_dict["preferences"] = updates.preferences
        
        profile = UserProfileStore.update_profile(user_id, update_dict)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users/{user_id}/visited")
def add_visited_country(user_id: str, country: str, visit_date: Optional[str] = None):
    """Add a visited country to user profile"""
    try:
        profile = UserProfileStore.add_visited_country(user_id, country, visit_date)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return {
            "message": f"Added {country} to visited countries",
            "visited_countries": profile["visited_countries"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-travel-data")
async def upload_travel_data(file: UploadFile = File(...)):
    """Upload travel guides, articles, or other travel data for RAG"""
    try:
        content = await file.read()
        filename = file.filename or "unknown"
        
        # Extract text
        if filename.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        elif filename.lower().endswith('.txt'):
            text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Chunk text
        chunks = []
        chunk_size = 500
        overlap = 50
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - overlap
        
        # Determine document type from filename or content
        doc_type = "general"
        if "activity" in filename.lower() or "things to do" in text.lower()[:500]:
            doc_type = "activity"
        elif "destination" in filename.lower() or "country guide" in text.lower()[:500]:
            doc_type = "destination"
        
        # Create metadata
        metadata = [{
            "source": filename,
            "type": doc_type,
            "chunk_id": i,
            "uploaded_at": datetime.now().isoformat()
        } for i in range(len(chunks))]
        
        # Add to vector store
        vector_store.add_documents(chunks, metadata)
        
        return {
            "message": f"Successfully processed {filename}",
            "chunks_added": len(chunks),
            "type": doc_type
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "gemini_configured": gemini_model is not None,
        "embedding_model_loaded": embedding_model is not None,
        "documents_loaded": len(vector_store.documents)
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("✈️  Starting Travel Buddy RAG API Server")
    print("="*60)
    print(f"📍 Server: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🔑 Gemini API Key Set: {bool(GEMINI_API_KEY)}")
    print(f"💾 Travel documents loaded: {len(vector_store.documents)}")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)