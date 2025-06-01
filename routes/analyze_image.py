from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
from io import BytesIO
from PIL import Image
from google import genai
import re
import json
import os
from dotenv import load_dotenv

from utils.prompts import generate_ai_analysis_prompt

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

router = APIRouter()

# Configure Gemini API
client = genai.Client(api_key=GEMINI_API_KEY)

class AnalyzeImageRequest(BaseModel):
    image_base64: str

@router.post("/analyze-image")
async def analyze_image(payload: AnalyzeImageRequest):
    try:
        print("📥 Step 1: Decode base64 image")
        image_data = base64.b64decode(payload.image_base64)
        image = Image.open(BytesIO(image_data))
        max_width = 800

        if image.width > max_width:
            ratio = max_width / float(image.width)
            new_height = int(float(image.height) * ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            print(f"📐 Image resized to: {image.size}")

        print("🧠 Step 2: Build prompt")
        prompt = generate_ai_analysis_prompt()

        print("📤 Step 3: Send image + prompt to Gemini")
        response = client.models.generate_content(
            model="gemini-2.5-pro-preview-03-25",  
            contents=[image, prompt]
        )

        print("📥 Step 4: Extract JSON from Gemini response")
        response_text = response.text.strip()
        print("📤 Gemini Response:\n", response_text)

        match = re.search(r'{.*}', response_text, re.DOTALL)
        if not match:
            print("⚠️ No JSON found")
            return {
                "error": "Unable to detect a valid meal in the image.",
                "invalid_input": True
            }

        parsed = json.loads(match.group())

        if not parsed.get("meal_data") or not parsed["meal_data"].get("name"):
            print("⚠️ Missing meal_data or name field")
            return {
                "error": "Could not confidently identify food in this image.",
                "invalid_input": True
            }

        print("✅ Success")
        return parsed

    except Exception as e:
        print("❌ Server Error:", str(e))
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
