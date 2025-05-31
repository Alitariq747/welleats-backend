from fastapi import APIRouter
from schemas.meal_log_model import UserMealLogRequest
from utils.meal_log_utils import generate_meal_log_from_text

router = APIRouter()

@router.post("/generate-meal-log-from-text")
async def meal_log_text_route(request: UserMealLogRequest):
    return await generate_meal_log_from_text(request.meal_description)

