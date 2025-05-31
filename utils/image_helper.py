import requests
from io import BytesIO
from fastapi import HTTPException
import re
import unicodedata
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from utils.supabase_helper import supabase, SUPABASE_BUCKET, SUPABASE_PUBLIC_URL
from supabase import StorageException

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Gemini config
client = genai.Client(api_key=GEMINI_API_KEY)


def get_deterministic_filename(meal_name: str) -> str:
    normalized = unicodedata.normalize("NFKD", meal_name).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^\w\s-]", "", normalized).strip().lower()
    slug = re.sub(r"[\s_-]+", "_", slug)
    return f"{slug}.png"


def check_supabase_image(meal_name: str):
    meal_file_name = get_deterministic_filename(meal_name)
    image_url = f"{SUPABASE_PUBLIC_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{meal_file_name}"

    response = requests.get(image_url)
    if response.status_code == 200:
        return image_url
    return None

def upload_to_supabase(meal_name, image_data):
    meal_file_name = get_deterministic_filename(meal_name)
    try:
        response = supabase.storage.from_("meal_images").upload(meal_file_name, image_data)
        if isinstance(response, StorageException):
            print("❌ Supabase Upload Error:", response.message)
            return None
        return f"{SUPABASE_PUBLIC_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{meal_file_name}"
    except Exception as e:
        print("❌ Unexpected Error During Upload:", str(e))
        return None

# image_helper.py


def generate_image_from_gemini(meal_name: str):
    prompt = f"A realistic, high-quality photo of {meal_name} served beautifully on a plate. Clean background."

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data  # ⬅️ binary image bytes

    return None  # ❌ no image generated



async def generate_meal_image(meal_name: str):
    # ✅ Step 1: Check Supabase
    existing_image_url = check_supabase_image(meal_name)
    if existing_image_url:
        return {"image_url": existing_image_url}

    # ✅ Step 2: Generate using Gemini
    generated_image_data = generate_image_from_gemini(meal_name)
    if not generated_image_data:
        raise HTTPException(status_code=500, detail="Gemini failed to generate image")

    # ✅ Step 3: Upload to Supabase
    stored_url = upload_to_supabase(meal_name, generated_image_data)
    if not stored_url:
        raise HTTPException(status_code=500, detail="Image upload failed")

    return {"image_url": stored_url}
