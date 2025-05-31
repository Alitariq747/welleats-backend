from fastapi import APIRouter
from schemas.recipe_model import RecipeRequest
from utils.recipe_utils import generate_recipe_from_leftovers

router = APIRouter()
@router.post("/generate-recipe-from-leftovers")
async def generate_recipe_route(request: RecipeRequest):
    return await generate_recipe_from_leftovers(request)