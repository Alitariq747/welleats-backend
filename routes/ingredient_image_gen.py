from fastapi import APIRouter
from utils.ingredient_image_utils import generate_ingredient_image

router = APIRouter()

@router.get("/generate-ingredient-image")
async def generate_ingredient_image_route(ingredient_name: str):
    """
    Generate an image of the ingredient using AI.
    """
    return await generate_ingredient_image(ingredient_name)
