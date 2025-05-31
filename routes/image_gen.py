from fastapi import APIRouter
from utils.image_helper import generate_meal_image

router = APIRouter()

@router.get("/generate-meal-image")
async def generate_meal_image_route(meal_name: str):
    return await generate_meal_image(meal_name)