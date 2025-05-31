from google import genai
from fastapi.responses import JSONResponse
import json
import os
from dotenv import load_dotenv
from utils.prompts import get_validation_prompt, get_meal_log_generation_prompt

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=GEMINI_API_KEY)

async def generate_meal_log_from_text(description: str):
    try:
        # ✅ Step 1: Validate input
        validation_prompt = get_validation_prompt(description)

        validation_response = client.models.generate_content(
    model="gemini-1.5-pro",
    contents=[validation_prompt]
)
        is_valid = validation_response.text.strip().lower() == "yes"

        if not is_valid:
            return JSONResponse(
                content={
                    "log_data": None,
                    "message": "❌ Could not detect a valid meal description. Please try again with more detail."
                },
                status_code=200
            )

        # ✅ Step 2: Generate structured log
        generation_prompt = get_meal_log_generation_prompt(description)

        response = client.models.generate_content(
    model="gemini-2.5-pro-preview-03-25",
    contents=[generation_prompt]
)
        raw_text = response.text.strip()

        clean_json = raw_text.replace("```json", "").replace("```", "").strip()

        meal_data = json.loads(clean_json)

        if meal_data == "INVALID":
            return JSONResponse(
                content={"log_data": None, "message": "❌ Unable to detect a valid meal log."},
                status_code=200
            )

        print(f'Meal Data from AI: {meal_data}')
        return {"log_data": meal_data}

    except json.JSONDecodeError:
        return JSONResponse(
            content={"log_data": None, "message": "❌ Failed to parse AI response. Try again."},
            status_code=500,
        )
    except Exception as e:
        return JSONResponse(
            content={"log_data": None, "message": f"❌ Internal Error: {str(e)}"},
            status_code=500,
        )