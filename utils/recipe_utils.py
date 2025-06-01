from schemas.recipe_model import RecipeRequest
from fastapi.responses import JSONResponse
from google import genai
import json
import os
from dotenv import load_dotenv
from utils.prompts import generate_recipe_prompt

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


client = genai.Client(api_key=GEMINI_API_KEY)

async def generate_recipe_from_leftovers(request: RecipeRequest):
    print(f"📥 Received recipe generation request: {request}")
    try:
        # 🧠 Prompt creation
        generation_prompt = generate_recipe_prompt(request)
        print(f"📝 Generated prompt:\n{generation_prompt}")

        # Choose model
        model_name = "gemini-2.5-pro-preview-03-25" if request.is_pro else "gemini-2.5-flash-preview-04-17-thinking"
        print(f"👉 Using Gemini model: {model_name}")

        # Call Gemini
        response = client.models.generate_content(
            model=model_name,
            contents=[generation_prompt]
        )
        raw_text = response.text.strip()
        print(f"🔙 Raw Gemini response:\n{raw_text}")

        # Clean JSON
        clean_json = raw_text.replace("```json", "").replace("```", "").strip()
        print(f"🧹 Cleaned JSON before parsing:\n{clean_json}")

        # Parse JSON
        recipe_data = json.loads(clean_json)
        print(f"✅ Successfully parsed recipe data:\n{recipe_data}")

        return {"recipe": recipe_data}

    except json.JSONDecodeError as e:
        print(f"❌ JSONDecodeError: {e}")
        print(f"🔎 Raw text received from Gemini:\n{raw_text}")
        return JSONResponse(
            status_code=500,
            content={"recipe": None, "message": "❌ Failed to parse Gemini response."}
        )
    except Exception as e:
        print(f"🔥 Exception occurred: {e}")
        return JSONResponse(
            status_code=500,
            content={"recipe": None, "message": f"❌ Internal Server Error: {str(e)}"}
        )

