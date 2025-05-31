import requests
import os
from io import BytesIO
from supabase import create_client, Client
from fastapi import HTTPException
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


SUPABASE_PUBLIC_URL=os.getenv('SUPABASE_URL')
SUPABASE_PUBLIC_KEY=os.getenv('SUPABASE_KEY')
SUPABASE_BUCKET_INGREDIENTS = "ingredients"  
supabase: Client = create_client(SUPABASE_PUBLIC_URL, SUPABASE_PUBLIC_KEY)

HUGGING_FACE_ACCESS_TOKEN=os.getenv('HUGGING_FACE_API_KEY')
HUGGING_FACE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


def check_supabase_image_ingredient(ingredient_name: str):
    """Check if the ingredient image already exists in Supabase Storage."""
    ingredient_file_name = f"{ingredient_name.replace(' ', '_')}.png"
    image_url = f"{SUPABASE_PUBLIC_URL}/storage/v1/object/public/{SUPABASE_BUCKET_INGREDIENTS}/{ingredient_file_name}"

    # ✅ Test if file exists
    response = requests.get(image_url)
    if response.status_code == 200:
        return image_url
    return None

def fetch_spoonacular_image(ingredient_name: str):
    """Fetch ingredient image from Spoonacular API."""
    url = f"https://api.spoonacular.com/food/ingredients/search?query={ingredient_name}&apiKey={SPOONACULAR_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            ingredient_name = data["results"][0]["name"].replace(" ", "-").lower()
            image_url = f"https://spoonacular.com/cdn/ingredients_100x100/{ingredient_name}.jpg"

            # ✅ Verify if Spoonacular Image Exists
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                print("Image returned from spoonacular")
                return image_url  # ✅ Return valid image URL
            else:
                print(f"❌ Spoonacular returned missing image for {ingredient_name}")
                return None
    return None

def download_image_data_ingredient(image_url):
    """Download image from URL and return binary data."""
    if not image_url:
        return None  # ✅ If image_url is None, return None immediately
    
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        return image_data.getvalue()
    except requests.RequestException as e:
        print(f"❌ Error downloading image: {e}")
        return None
        

def generate_ingredient_image_from_gemini(ingredient_name: str):
      """Generate an AI ingredient image using Hugging Face Stable Diffusion."""
      prompt = (
        f"A clear, isolated stock photo of {ingredient_name}, sliced or whole, "
        f"on a clean white background. The ingredient should be fresh, realistic, "
        f"and photographed from a top-down or slightly angled view. No shadows, no additional objects. "
        f"The image should have a smooth, uniform white background similar to stock grocery images. "
        f"Ensure it is a small, centered object with no extra styling. "
        f"The image should be crisp, sharp, and look like a real food stock image. "
        f"Size should be 100x100 pixels, perfectly framed, no blur or artistic details."
    )

      response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

      for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data  # ⬅️ binary image bytes

      return None  # ❌ no image generated


def upload_to_supabase_ingredient(ingredient_name, image_data):
    """Upload image to Supabase Storage and return public URL."""
    if not image_data:
        print("❌ Skipping Supabase upload - No valid image data")
        return None    
    ingredient_file_name = f"{ingredient_name.replace(' ', '_')}.png"
    storage_path = f"{ingredient_file_name}"

    try:
        # ✅ Upload image to Supabase
        response = supabase.storage.from_("ingredients").upload(storage_path, image_data)

        # ✅ Handle errors
        if isinstance(response, Exception):
            print("❌ Supabase Upload Error:", response)
            return None

        # ✅ Return public URL
        return f"{SUPABASE_PUBLIC_URL}/storage/v1/object/public/{SUPABASE_BUCKET_INGREDIENTS}/{storage_path}"
    
    except Exception as e:
        print("❌ Unexpected Upload Error:", str(e))
        return None

async def generate_ingredient_image(ingredient_name: str):
    """Fetch or generate an ingredient image and store it in Supabase."""

    # Check Supabase Storage First
    existing_image_url = check_supabase_image_ingredient(ingredient_name)
    if existing_image_url:
        return {"image_url": existing_image_url}

    #  Try Fetching from Free API (Spoonacular)
    spoonacular_image_url = fetch_spoonacular_image(ingredient_name)
    if spoonacular_image_url:
        image_data = download_image_data_ingredient(spoonacular_image_url)
        if image_data:
            stored_url = upload_to_supabase_ingredient(ingredient_name, image_data)
            return {"image_url": stored_url or spoonacular_image_url}

  

    # ✅ Step 4: Generate Using Hugging Face AI
    generated_image_data = generate_ingredient_image_from_gemini(ingredient_name)
    if not generated_image_data:
        raise HTTPException(status_code=500, detail="Failed to generate AI image")
    
    if not isinstance(generated_image_data, bytes):
        print("❌ AI Image Generation Error: Expected bytes, received", type(generated_image_data))
        raise HTTPException(status_code=500, detail="Invalid AI image format")

    # ✅ Step 5: Upload AI Image to Supabase
    stored_url = upload_to_supabase_ingredient(ingredient_name, generated_image_data)
    if stored_url:
        return {"image_url": stored_url}