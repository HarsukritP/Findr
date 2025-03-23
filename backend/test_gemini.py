import os
import pathlib
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
current_dir = pathlib.Path(__file__).parent.resolve()
load_dotenv(current_dir / ".env")

# Set credentials path if not already set
creds_path = str(current_dir / "gcp_key.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

# Check if credentials are set
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    print("✅ GOOGLE_APPLICATION_CREDENTIALS is set!")
    print(f"Path: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")
else:
    print("❌ GOOGLE_APPLICATION_CREDENTIALS is NOT set!")

# Check for API key in environment
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print("✅ GEMINI_API_KEY is set from .env file!")
else:
    print("❌ GEMINI_API_KEY is not set in .env file! Please add it to backend/.env:")
    print("GEMINI_API_KEY=your_actual_api_key")
    print("\nExiting test.")
    exit(1)

# Configure Gemini AI
try:
    # Configure the API
    genai.configure(api_key=api_key)
    
    # Test Gemini AI with a simple prompt
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Summarize the impact of AI in healthcare.")
    
    print("\n✅ Gemini AI Test Successful!")
    print("Response:", response.text)
    
except Exception as e:
    print("\n❌ Gemini API Test Failed!")
    print("Error:", e) 