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
    print(f'Recieved recipe generation request: {request}')
    try:

        # 🧠 Prompt creation
        generation_prompt = generate_recipe_prompt(request)

        if request.is_pro:
            model_name = "gemini-2.5-pro-preview-03-25"
        else:
            model_name =  "gemini-2.5-flash-preview-04-17-thinking"
        
        print(f'Since request is {request.is_pro} so using ${model_name}')
        # 🧠 Call Gemini
        response = client.models.generate_content(
    model=model_name,
    contents=[generation_prompt]
)
        raw_text = response.text.strip()

        # ✅ Clean markdown if present
        clean_json = raw_text.replace("```json", "").replace("```", "").strip()

        recipe_data = json.loads(clean_json)

        return { "recipe": recipe_data }

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=500,
            content={ "recipe": None, "message": "❌ Failed to parse Gemini response." }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={ "recipe": None, "message": f"❌ Internal Server Error: {str(e)}" }
        )
