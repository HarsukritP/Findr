import os
import pathlib
import base64
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import vision
from google.cloud.vision_v1 import types
import google.generativeai as genai
import io
from pymongo import MongoClient
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
from bson import ObjectId
import PyPDF2

# Load environment variables from .env file
current_dir = pathlib.Path(__file__).parent.resolve()
load_dotenv(current_dir / ".env")

# Set Google Cloud credentials with absolute path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(current_dir / "gcp_key.json")

# Configure Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    print("✅ GEMINI_API_KEY loaded from .env file")
    genai.configure(api_key=gemini_api_key)
else:
    print("❌ GEMINI_API_KEY not found in .env file")

# MongoDB setup
try:
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise Exception("MONGODB_URI not found in .env file")
    print(f"Attempting to connect to MongoDB with URI: {mongodb_uri}")
    
    client = MongoClient(mongodb_uri)
    db = client["findr"]
    users_collection = db.users
    swipes_collection = db.swipes
    matches_collection = db.matches
    
    # Test the connection
    server_info = client.server_info()
    print("✅ Successfully connected to MongoDB")
    print(f"MongoDB version: {server_info.get('version', 'unknown')}")
    
    # List all databases
    databases = client.list_database_names()
    print(f"Available databases: {databases}")
    
    # List collections in findr database
    collections = db.list_collection_names()
    print(f"Collections in findr database: {collections}")
    
    # Count documents in collections
    users_count = users_collection.count_documents({})
    swipes_count = swipes_collection.count_documents({})
    matches_count = matches_collection.count_documents({})
    print(f"Collection counts:")
    print(f"- Users: {users_count}")
    print(f"- Swipes: {swipes_count}")
    print(f"- Matches: {matches_count}")
    
except Exception as e:
    print(f"❌ MongoDB connection error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    print(f"Error details: {str(e)}")
    raise Exception(f"Failed to connect to MongoDB: {str(e)}")

# Google Client ID
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UserCreate(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    name: str
    skills: List[str]
    experience: List[str]
    tags: List[str]
    background: str
    school: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    background: Optional[str] = None
    school: Optional[str] = None

class SwipeRequest(BaseModel):
    swiped_id: str
    liked: bool

@app.get("/")
def home():
    return {"message": "Yo Macha! Python backend linked to React!"}


# Authentication endpoints
@app.post("/register")
async def register(user: UserCreate):
    # Check if user already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user document
    new_user = {
        "email": user.email,
        "password": user.password,  # In production, hash this password!
        "created_at": datetime.utcnow(),
        "profile_completed": False
    }
    
    result = users_collection.insert_one(new_user)
    
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }

@app.post("/login")
async def login(user: UserCreate):
    try:
        print(f"Login attempt for email: {user.email}")  # Debug log
        
        # Find user in database
        db_user = users_collection.find_one({"email": user.email})
        print(f"Found user: {db_user is not None}")  # Debug log
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if db_user["password"] != user.password:  # In production, verify hashed password
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Convert ObjectId to string for response
        user_id = str(db_user["_id"])
        profile_completed = db_user.get("profile_completed", False)
        
        print(f"Login successful for user_id: {user_id}")  # Debug log
        
        return {
            "message": "Login successful",
            "user_id": user_id,
            "profile_completed": profile_completed
        }
        
    except HTTPException as he:
        print(f"HTTP error during login: {str(he)}")  # Debug log
        raise he
    except Exception as e:
        print(f"Unexpected error during login: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error during login: {str(e)}"
        )

# Profile management endpoints
@app.post("/profile/{user_id}")
async def create_profile(user_id: str, profile: UserProfile):
    try:
        # Convert string user_id to ObjectId
        object_id = ObjectId(user_id)
        
        # Update user profile
        result = users_collection.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "name": profile.name,
                    "skills": profile.skills,
                    "experience": profile.experience,
                    "tags": profile.tags,
                    "background": profile.background,
                    "school": profile.school,
                    "profile_completed": True
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "Profile created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format or database error: {str(e)}"
        )

@app.get("/profiles")
async def get_profiles(skip: int = 0, limit: int = 10):
    try:
        # Get all profiles
        profiles = list(users_collection.find(
            {"profile_completed": True},  # Only get documents that have a completed profile
            {
                "_id": 1,
                "name": 1,
                "skills": 1,
                "experience": 1,
                "tags": 1,
                "background": 1,
                "school": 1
            }
        ).skip(skip).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for profile in profiles:
            profile["_id"] = str(profile["_id"])
        
        print("Fetched profiles:", profiles)  # Debug log
        return profiles
    except Exception as e:
        print("Error fetching profiles:", str(e))  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    try:
        # Convert string user_id to ObjectId
        object_id = ObjectId(user_id)
        
        # Get user profile
        user = users_collection.find_one(
            {"_id": object_id},
            {
                "_id": 1,
                "name": 1,
                "skills": 1,
                "experience": 1,
                "tags": 1,
                "background": 1,
                "school": 1,
                "profile_completed": 1
            }
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        print("Fetched user profile:", user)  # Debug log
        
        # Convert ObjectId to string for JSON serialization
        user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        print("Error fetching profile:", str(e))  # Debug log
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format or database error: {str(e)}"
        )

@app.post("/analyze-resume/{user_id}")
async def analyze_resume(user_id: str, file: UploadFile = File(...)):
    try:
        # Read the file content
        content = await file.read()
        
        # Extract text based on file type
        if file.filename.endswith('.pdf'):
            # Handle PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            document_text = ""
            for page in pdf_reader.pages:
                document_text += page.extract_text()
        else:
            # Handle image using Google Vision
            vision_client = vision.ImageAnnotatorClient()
            image = types.Image(content=content)
            response = vision_client.text_detection(image=image)
            texts = response.text_annotations
            
            if not texts:
                raise HTTPException(
                    status_code=400,
                    detail="No text detected in the document"
                )
            document_text = texts[0].description
        
        if not document_text:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document"
            )
        
        print("Extracted text:", document_text[:500])  # Debug log
        
        # Initialize Gemini
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        def clean_json_response(response_text):
            # Remove any markdown formatting or extra text
            text = response_text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            return text
        
        try:
            # Extract basic information
            basic_prompt = """
            Given the following resume text, extract ONLY the person's full name, education/school, and a brief background summary.
            
            Output the information in this EXACT format (do not include any other text or explanation):
            {"name": "John Smith", "school": "University Name", "background": "Brief background"}
            
            Resume text:
            """ + document_text
            
            basic_response = gemini_model.generate_content(basic_prompt)
            basic_text = clean_json_response(basic_response.text)
            print("Basic response:", basic_text)  # Debug log
            basic_data = json.loads(basic_text)
            
            # Extract skills
            skills_prompt = """
            Extract a list of technical and soft skills from this resume.
            
            Output ONLY a JSON array in this EXACT format (no other text):
            ["Python", "JavaScript", "Leadership"]
            
            Resume text:
            """ + document_text
            
            skills_response = gemini_model.generate_content(skills_prompt)
            skills_text = clean_json_response(skills_response.text)
            print("Skills response:", skills_text)  # Debug log
            skills_data = json.loads(skills_text)
            
            # Extract experience
            experience_prompt = """
            Extract the main experiences (jobs, internships, projects) from this resume.
            
            Output ONLY a JSON array in this EXACT format (no other text):
            ["Software Engineer at Company X", "Web Development Intern", "Machine Learning Project"]
            
            Resume text:
            """ + document_text
            
            experience_response = gemini_model.generate_content(experience_prompt)
            experience_text = clean_json_response(experience_response.text)
            print("Experience response:", experience_text)  # Debug log
            experience_data = json.loads(experience_text)
            
            # Generate tags
            tags_prompt = """
            Based on this resume, generate relevant tags for hackathon team matching.
            Include technical areas, interests, and potential roles.
            
            Output ONLY a JSON array in this EXACT format (no other text):
            ["Frontend", "AI/ML", "Team Lead"]
            
            Resume text:
            """ + document_text
            
            tags_response = gemini_model.generate_content(tags_prompt)
            tags_text = clean_json_response(tags_response.text)
            print("Tags response:", tags_text)  # Debug log
            tags_data = json.loads(tags_text)
            
        except json.JSONDecodeError as e:
            print("JSON decode error:", str(e))  # Debug log
            print("Failed response text:", basic_response.text)  # Debug log
            raise HTTPException(
                status_code=500,
                detail="Failed to parse AI response. Please try again."
            )
        except Exception as e:
            print("Error in AI processing:", str(e))  # Debug log
            raise HTTPException(
                status_code=500,
                detail="Error processing resume with AI. Please try again."
            )
        
        # Combine all data
        profile_data = {
            "name": basic_data["name"],
            "school": basic_data["school"],
            "background": basic_data["background"],
            "skills": skills_data,
            "experience": experience_data,
            "tags": tags_data
        }
        
        print("Final profile data:", profile_data)  # Debug log
        
        # Update user's profile in MongoDB
        object_id = ObjectId(user_id)
        result = users_collection.update_one(
            {"_id": object_id},
            {
                "$set": {
                    **profile_data,
                    "profile_completed": True,
                    "ai_generated": True,
                    "last_updated": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        return {
            "message": "Profile generated successfully",
            "profile": profile_data
        }
        
    except Exception as e:
        print(f"Error in analyze_resume: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )

# Swiping and matching endpoints
@app.post("/swipe/{user_id}")
async def swipe(user_id: str, swipe_data: SwipeRequest):
    try:
        # Convert string IDs to ObjectId
        swiper_id = ObjectId(user_id)
        swiped_id = ObjectId(swipe_data.swiped_id)
        
        # Record the swipe
        swipe_record = {
            "swiper_id": swiper_id,
            "swiped_id": swiped_id,
            "liked": swipe_data.liked,  # Always use 'liked' field
            "timestamp": datetime.utcnow()
        }
        swipes_collection.insert_one(swipe_record)
        
        # Check if it's a match
        match_created = False
        if swipe_data.liked:
            # Check if the other person has already liked this user
            other_swipe = swipes_collection.find_one({
                "swiper_id": swiped_id,
                "swiped_id": swiper_id,
                "$or": [
                    {"liked": True},
                    {"action": "right"}  # Handle legacy swipes
                ]
            })
            
            if other_swipe:
                # Create a match
                match_record = {
                    "user1_id": swiper_id,
                    "user2_id": swiped_id,
                    "timestamp": datetime.utcnow()
                }
                matches_collection.insert_one(match_record)
                match_created = True
        
        return {"success": True, "match_created": match_created}
        
    except Exception as e:
        print(f"Error in swipe endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing swipe: {str(e)}"
        )

@app.get("/matches/{user_id}")
async def get_matches(user_id: str):
    try:
        # Convert string ID to ObjectId
        user_oid = ObjectId(user_id)
        
        # Find all matches where this user is either user1 or user2
        matches = []
        match_records = matches_collection.find({
            "$or": [
                {"user1_id": user_oid},
                {"user2_id": user_oid}
            ]
        })
        
        for match in match_records:
            # Determine which user is the matched user
            other_user_id = match["user2_id"] if match["user1_id"] == user_oid else match["user1_id"]
            matched_user = users_collection.find_one({"_id": other_user_id})
            
            if matched_user:
                # Convert ObjectId to string for JSON serialization
                matched_user["_id"] = str(matched_user["_id"])
                matches.append({
                    "matched_user": matched_user,
                    "timestamp": match["timestamp"]
                })
        
        return matches
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching matches: {str(e)}"
        )

@app.get("/pending-matches/{user_id}")
async def get_pending_matches(user_id: str):
    try:
        # Convert string ID to ObjectId
        user_oid = ObjectId(user_id)
        
        # Find all pending matches (both incoming and outgoing)
        pending_profiles = []
        
        # Find users who you've swiped right on (outgoing)
        outgoing_swipes = swipes_collection.find({
            "swiper_id": user_oid,
            "$or": [
                {"liked": True},
                {"action": "right"}
            ]
        })
        
        for swipe in outgoing_swipes:
            # Check if the other person has rejected
            other_swipe = swipes_collection.find_one({
                "swiper_id": swipe["swiped_id"],
                "swiped_id": user_oid,
                "$or": [
                    {"liked": False},
                    {"action": "left"}
                ]
            })
            
            # If no response yet and no match exists
            if not other_swipe:
                match_exists = matches_collection.find_one({
                    "$or": [
                        {"user1_id": user_oid, "user2_id": swipe["swiped_id"]},
                        {"user1_id": swipe["swiped_id"], "user2_id": user_oid}
                    ]
                })
                
                if not match_exists:
                    other_user = users_collection.find_one({"_id": swipe["swiped_id"]})
                    if other_user:
                        other_user["_id"] = str(other_user["_id"])
                        pending_profiles.append({
                            "user": other_user,
                            "timestamp": swipe["timestamp"],
                            "type": "outgoing"  # You swiped right on them
                        })
        
        # Find users who have swiped right on you (incoming)
        incoming_swipes = swipes_collection.find({
            "swiped_id": user_oid,
            "$or": [
                {"liked": True},
                {"action": "right"}
            ]
        })
        
        for swipe in incoming_swipes:
            # Check if you haven't responded yet
            your_swipe = swipes_collection.find_one({
                "swiper_id": user_oid,
                "swiped_id": swipe["swiper_id"]
            })
            
            # Only include if you haven't swiped yet and no match exists
            if not your_swipe:
                match_exists = matches_collection.find_one({
                    "$or": [
                        {"user1_id": user_oid, "user2_id": swipe["swiper_id"]},
                        {"user1_id": swipe["swiper_id"], "user2_id": user_oid}
                    ]
                })
                
                if not match_exists:
                    other_user = users_collection.find_one({"_id": swipe["swiper_id"]})
                    if other_user:
                        other_user["_id"] = str(other_user["_id"])
                        pending_profiles.append({
                            "user": other_user,
                            "timestamp": swipe["timestamp"],
                            "type": "incoming"  # They swiped right on you
                        })
        
        print("Pending profiles:", pending_profiles)  # Debug log
        return pending_profiles
        
    except Exception as e:
        print(f"Error in pending matches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching pending matches: {str(e)}"
        )

# Initialize MongoDB collections at startup
@app.on_event("startup")
async def startup_event():
    global users_collection, swipes_collection, matches_collection
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client.findr
    users_collection = db.users
    swipes_collection = db.swipes
    matches_collection = db.matches

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 