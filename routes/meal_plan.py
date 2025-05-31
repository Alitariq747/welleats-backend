from google import genai
import re
import json

from schemas.meal_plan_model import MealRequest
from fastapi import APIRouter
import os
from dotenv import load_dotenv
from utils.prompts import generate_meal_plan_prompt

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=GEMINI_API_KEY)

router = APIRouter()

@router.post("/generate-meals")
async def generate_meal_plan(request: MealRequest):
    print("✅ Received Meal Request:", request.model_dump())
    
    eating_frequency_mapping = {
        "three_meals": 3,
        "two_meals": 2,
        "intermittent_fasting": 2,
        "small_frequent_meals": 5,
        "one_large_meal": 1,
    }

    request.meal_count = eating_frequency_mapping.get(request.eating_frequency, 3)
    if request.is_pro:
        if request.regenerate_count == 0:
            model_name = "gemini-2.5-pro-preview-03-25"
        elif request.regenerate_count % 2 != 0:
            model_name =  "gemini-2.5-flash-preview-04-17-thinking"
        else:
            model_name =  "gemini-2.5-pro-preview-03-25"       
        
    else:
        model_name = "gemini-2.5-flash-preview-04-17-thinking"    
      


    print(f"🔁 Using Gemini Model: {model_name}")
    print('Regenerate count = ', request.regenerate_count)

    prompt = generate_meal_plan_prompt(request=request)
       
    try:
        response = client.models.generate_content(
    model=model_name,
    contents=[prompt],
  
)
        ai_response = response.text.strip()
        print(f"🛠 DEBUG: Raw AI Response:\n{ai_response}")

        clean_json = re.sub(r"```json\n|\n```", "", ai_response).strip()

        meals = json.loads(clean_json)

        return {"meals": meals}

    except json.JSONDecodeError as e:
        print(f"⚠️ JSON Decode Error: {e}")
        return {"error": "Failed to parse AI response. Ensure model outputs valid JSON."}
    except Exception as e:
        return {"error": str(e)}