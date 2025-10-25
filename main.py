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
        # Try different models in order of preference
        model_names = ['gemini-2.0-flash-lite', 'gemini-1.5-flash', 'gemini-pro']
        gemini_model = None
        for model_name in model_names:
            try:
                gemini_model = genai.GenerativeModel(model_name)
                print(f"✅ Gemini configured with model: {model_name}")
                break
            except Exception as model_error:
                print(f"⚠️ Failed to load {model_name}: {model_error}")
                continue
        
        if gemini_model is None:
            print("❌ No available Gemini models found")
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
            "Chat interface",
            "Interactive travel map"
        ]
    }

@app.get("/api/health")
def health_check():
    gemini_status = gemini_model is not None
    api_key_set = bool(os.getenv("GEMINI_API_KEY"))
    
    return {
        "status": "healthy",
        "gemini_configured": gemini_status,
        "api_key_set": api_key_set,
        "users": len(user_profiles),
        "debug": {
            "has_model": gemini_status,
            "has_key": api_key_set,
            "key_preview": os.getenv("GEMINI_API_KEY", "")[:10] + "..." if api_key_set else "NOT SET"
        }
    }

@app.get("/api/test")
def test_endpoint():
    """Simple test endpoint to verify API is working"""
    return {
        "message": "API is working!",
        "gemini_ready": gemini_model is not None,
        "endpoints": {
            "health": "/api/health (GET)",
            "activities": "/api/activities (POST)",
            "countries": "/api/recommend-countries (POST)",
            "translate": "/api/translate (POST)",
            "chat": "/api/chat (POST)",
            "map": "/api/users/{user_id}/visited (POST/DELETE)"
        }
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Universal chat endpoint - handles all queries"""
    try:
        # Check if Gemini is configured
        if gemini_model is None:
            return {
                "response": "Gemini API is not configured. Please set GEMINI_API_KEY environment variable.",
                "user_id": request.user_id
            }
        
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
        print(f"❌ Error in chat: {str(e)}")
        return {
            "response": f"Sorry, I encountered an error: {str(e)}",
            "user_id": request.user_id
        }

@app.post("/api/activities")
async def get_activities(request: ActivityRequest):
    """Get activity recommendations"""
    try:
        # Check if Gemini is configured
        if gemini_model is None:
            return {
                "response": "Gemini API is not configured. Please check GEMINI_API_KEY environment variable.",
                "recommendations": [],
                "sources": []
            }
        
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
        print(f"❌ Error in get_activities: {str(e)}")
        return {
            "response": f"Error: {str(e)}",
            "recommendations": [],
            "sources": []
        }

@app.post("/api/recommend-countries")
async def recommend_countries(request: CountryRecommendationRequest):
    """Recommend countries based on user's travel history"""
    try:
        # Check if Gemini is configured
        if gemini_model is None:
            return {
                "response": "Gemini API is not configured. Please check GEMINI_API_KEY environment variable.",
                "recommendations": [],
                "sources": []
            }
        
        profile = get_or_create_profile(request.user_id)
        visited = profile.get('visited_countries', [])
        visited_str = ", ".join(visited) if visited else "None - this is their first trip"
        
        # Build a more detailed prompt based on travel history
        if visited:
            context = f"""The user has previously visited: {visited_str}

Based on their travel history, recommend countries that:
1. Offer similar experiences but in new regions
2. Are a natural progression in travel difficulty/adventure
3. Complement their existing travel experiences
4. Avoid repeating the same country or very similar destinations"""
        else:
            context = """This is the user's first major trip! Recommend:
1. Countries that are beginner-friendly for international travel
2. Destinations with good infrastructure and English speakers
3. Safe and welcoming places for first-time travelers
4. Diverse experiences to help them discover their travel style"""
        
        prompt = f"""You are an expert travel advisor with deep knowledge of world destinations.

User's Travel Profile:
- Previously visited countries: {visited_str}
- Budget preference: {request.budget}
- Travel style: {request.travel_style or 'diverse experiences'}

{context}

Task: Recommend 5 countries for their NEXT trip. Make sure these are countries they HAVEN'T visited yet.

For each recommendation:
- Explain WHY it's a good fit based on their previous travels
- If they have travel history, mention similarities to places they've enjoyed
- Highlight what makes it different from places they've been
- Consider their budget and travel style

Return ONLY a JSON array (no markdown, no code blocks):
[
  {{
    "country": "Country name",
    "reason": "Detailed reason why this matches their profile, referencing their previous travels if applicable (3-4 sentences)",
    "highlights": ["specific highlight 1", "specific highlight 2", "specific highlight 3"],
    "best_for": "what type of experiences they'll find here",
    "estimated_budget": "$50-80/day" or similar realistic range,
    "best_season": "specific months, e.g., April-October",
    "similar_to": "which of their visited countries it resembles, if applicable - OTHERWISE leave empty string"
  }}
]

Important: 
- Do NOT recommend countries they've already visited
- Make recommendations diverse and interesting
- Be specific with details, not generic"""

        response_text = generate_gemini_response(prompt)
        recommendations = parse_json_from_text(response_text, "array")
        
        # Filter out any countries they've already visited (safety check)
        if visited:
            visited_lower = [c.lower() for c in visited]
            recommendations = [
                rec for rec in recommendations 
                if rec.get('country', '').lower() not in visited_lower
            ]
        
        return {
            "response": response_text,
            "recommendations": recommendations,
            "sources": []
        }
    
    except Exception as e:
        print(f"❌ Error in recommend_countries: {str(e)}")
        return {
            "response": f"Error: {str(e)}",
            "recommendations": [],
            "sources": []
        }

@app.post("/api/translate")
async def translate_text(request: TranslationRequest):
    """Translate text"""
    try:
        # Check if Gemini is configured
        if gemini_model is None:
            return {
                "translation": "Gemini API not configured",
                "pronunciation": "",
                "cultural_note": "Please check GEMINI_API_KEY",
                "formality": "neutral"
            }
        
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
        print(f"❌ Error in translate_text: {str(e)}")
        return {
            "translation": f"Error: {str(e)}",
            "pronunciation": "",
            "cultural_note": "",
            "formality": "neutral"
        }

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
        
        # Normalize country name (capitalize properly)
        country = country.strip().title()
        
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

@app.post("/api/users/{user_id}/visited/bulk")
def add_multiple_visited_countries(user_id: str, countries: List[str]):
    """Add multiple visited countries at once"""
    try:
        profile = get_or_create_profile(user_id)
        
        added_count = 0
        for country in countries:
            country = country.strip().title()
            if country and country not in profile["visited_countries"]:
                profile["visited_countries"].append(country)
                profile["travel_history"].append({
                    "country": country,
                    "visit_date": datetime.now().isoformat()
                })
                added_count += 1
        
        user_profiles[user_id] = profile
        
        return {
            "message": f"Added {added_count} countries",
            "visited_countries": profile["visited_countries"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/users/{user_id}/visited/{country}")
def remove_visited_country(user_id: str, country: str):
    """Remove a country from visited list"""
    try:
        profile = get_or_create_profile(user_id)
        
        if country in profile["visited_countries"]:
            profile["visited_countries"].remove(country)
            user_profiles[user_id] = profile
            
            return {
                "message": f"Removed {country} from visited countries",
                "visited_countries": profile["visited_countries"]
            }
        else:
            raise HTTPException(status_code=404, detail=f"{country} not found in visited countries")
    except HTTPException:
        raise
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