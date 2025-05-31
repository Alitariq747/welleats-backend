from pydantic import BaseModel


class UserMealLogRequest(BaseModel):
    meal_description: str