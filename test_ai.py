import os
from dotenv import load_dotenv
from google import genai

# Load the API key
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Check if API key exists
if not api_key:
    print("ERROR: Gemini API key was not found.")
    exit()

# Connect to Gemini
client = genai.Client(api_key=api_key)

# Test Gemini
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say exactly: Gemini connection is working!"
)

print(response.text)