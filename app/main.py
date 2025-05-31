from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware


from routes import meal_plan, image_gen, ingredient_image_gen, meal_log, recipe_gen, analyze_image

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
router = APIRouter()


app.include_router(meal_plan.router)
app.include_router(image_gen.router)   
app.include_router(ingredient_image_gen.router)
app.include_router(meal_log.router)
app.include_router(recipe_gen.router)
app.include_router(analyze_image.router)






