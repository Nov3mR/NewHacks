from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Travel Buddy API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini (lightweight)
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')  # Lighter model
        print("✅ Gemini configured")
    else:
        print("⚠️ GEMINI_API_KEY not set!")
        gemini_model = None
except Exception as e:
    print(f"❌ Error configuring Gemini: {e}")
    gemini_model = None

# In-memory storage (lightweight)
user_profiles = {}

# Pydantic models
class ActivityRequest(BaseModel):
    user_id: str
    country: str
    interests: Optional[List[str]] = []
    duration_days: Optional[int] = None

class CountryRecommendationRequest(BaseModel):
    user_id: str
    budget: Optional[str] = "moderate"
    travel_style: Optional[str] = None

class TranslationRequest(BaseModel):
    text: str
    target_language: str
    context: Optional[str] = None

class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[dict] = None

class UserProfileUpdate(BaseModel):
    visited_countries: Optional[List[str]] = None
    preferences: Optional[dict] = None

# Helper functions
def get_or_create_profile(user_id: str):
    if user_id not in user_profiles:
        user_profiles[user_id] = {
            "user_id": user_id,
            "visited_countries": [],
            "preferences": {},
            "travel_history": [],
            "created_at": datetime.now().isoformat()
        }
    return user_profiles[user_id]

def generate_gemini_response(prompt: str) -> str:
    if gemini_model is None:
        raise HTTPException(status_code=500, detail="Gemini model not configured")
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

def parse_json_from_text(text: str, expected_type: str = "array"):
    """Extract JSON from text response"""
    try:
        if expected_type == "array":
            json_start = text.find('[')
            json_end = text.rfind(']') + 1
        else:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = text[json_start:json_end]
            return json.loads(json_str)
        return [] if expected_type == "array" else {}
    except:
        return [] if expected_type == "array" else {}

# API Endpoints
@app.get("/")
def root():
    return {
        "message": "Travel Buddy API",
        "status": "running",
        "version": "2.0.0",
        "features": [
            "Activity recommendations",
            "Country recommendations", 
            "Translation service",
            "Chat interface"
        ]
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "gemini_configured": gemini_model is not None,
        "users": len(user_profiles)
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Universal chat endpoint - handles all queries"""
    try:
        profile = get_or_create_profile(request.user_id)
        
        prompt = f"""You are a helpful travel advisor chatbot. Answer the user's travel question naturally and helpfully.

User Profile:
- Visited countries: {', '.join(profile.get('visited_countries', [])) or 'None yet'}

User Question: {request.message}

Context: {json.dumps(request.context) if request.context else 'None'}

Provide a friendly, informative response. If giving recommendations, format them clearly with bullet points."""

        response_text = generate_gemini_response(prompt)
        
        return {
            "response": response_text,
            "user_id": request.user_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/activities")
async def get_activities(request: ActivityRequest):
    """Get activity recommendations"""
    try:
        profile = get_or_create_profile(request.user_id)
        
        interests_str = ", ".join(request.interests) if request.interests else "general sightseeing"
        duration_str = f" for {request.duration_days} days" if request.duration_days else ""
        
        prompt = f"""You are a travel advisor. Provide 5-7 activity recommendations for {request.country}.

User interests: {interests_str}
Duration: {duration_str}
Previously visited: {', '.join(profile.get('visited_countries', [])) or 'First trip'}

Return ONLY a JSON array (no markdown, no extra text):
[
  {{
    "name": "Activity name",
    "description": "Brief description (2-3 sentences)",
    "category": "adventure/cultural/food/nature/etc",
    "location": "specific location",
    "estimated_cost": "$/$$/$$$",
    "best_time": "best time to do this",
    "tips": "insider tip"
  }}
]"""

        response_text = generate_gemini_response(prompt)
        recommendations = parse_json_from_text(response_text, "array")
        
        return {
            "response": response_text,
            "recommendations": recommendations,
            "sources": []
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend-countries")
async def recommend_countries(request: CountryRecommendationRequest):
    """Recommend countries"""
    try:
        profile = get_or_create_profile(request.user_id)
        visited = profile.get('visited_countries', [])
        visited_str = ", ".join(visited) if visited else "None - first trip"
        
        prompt = f"""You are a travel advisor. Recommend 5 countries for the user's next trip.

User Profile:
- Visited: {visited_str}
- Budget: {request.budget}
- Style: {request.travel_style or 'mixed'}

Return ONLY a JSON array (no markdown):
[
  {{
    "country": "Country name",
    "reason": "Why this matches their profile (2-3 sentences)",
    "highlights": ["highlight 1", "highlight 2", "highlight 3"],
    "best_for": "type of traveler",
    "estimated_budget": "budget per day",
    "best_season": "best time to visit",
    "similar_to": "similar to their visited countries (if applicable)"
  }}
]"""

        response_text = generate_gemini_response(prompt)
        recommendations = parse_json_from_text(response_text, "array")
        
        return {
            "response": response_text,
            "recommendations": recommendations,
            "sources": []
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate")
async def translate_text(request: TranslationRequest):
    """Translate text"""
    try:
        context_note = f"\nContext: {request.context}" if request.context else ""
        
        prompt = f"""Translate to {request.target_language}.{context_note}

Text: "{request.text}"

Return ONLY a JSON object (no markdown):
{{
  "translation": "translated text",
  "pronunciation": "phonetic guide",
  "cultural_note": "usage tip",
  "formality": "formal/casual"
}}"""

        response_text = generate_gemini_response(prompt)
        translation = parse_json_from_text(response_text, "object")
        
        if not translation:
            translation = {
                "translation": response_text,
                "pronunciation": "",
                "cultural_note": "",
                "formality": "neutral"
            }
        
        return translation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}")
def get_user_profile(user_id: str):
    """Get user profile"""
    try:
        profile = get_or_create_profile(user_id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/users/{user_id}")
def update_user_profile(user_id: str, updates: UserProfileUpdate):
    """Update user profile"""
    try:
        profile = get_or_create_profile(user_id)
        
        if updates.visited_countries is not None:
            profile["visited_countries"] = updates.visited_countries
        if updates.preferences is not None:
            profile["preferences"] = updates.preferences
        
        profile["updated_at"] = datetime.now().isoformat()
        user_profiles[user_id] = profile
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users/{user_id}/visited")
def add_visited_country(user_id: str, country: str, visit_date: Optional[str] = None):
    """Add visited country"""
    try:
        profile = get_or_create_profile(user_id)
        
        if country not in profile["visited_countries"]:
            profile["visited_countries"].append(country)
        
        profile["travel_history"].append({
            "country": country,
            "visit_date": visit_date or datetime.now().isoformat()
        })
        
        user_profiles[user_id] = profile
        
        return {
            "message": f"Added {country} to visited countries",
            "visited_countries": profile["visited_countries"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run server
if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", 8000))
    print("\n" + "="*50)
    print("✈️  Travel Buddy API (Optimized)")
    print("="*50)
    print(f"📍 Server: http://0.0.0.0:{PORT}")
    print(f"🔑 Gemini: {'✅' if gemini_model else '❌'}")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT)