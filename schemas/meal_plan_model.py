from pydantic import BaseModel
from typing import List, Optional


class MealRequest(BaseModel):
    meal_goal: str
    dietary_preferences: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    region: str
    activity_level: str
    age: int
    gender: str
    portion_size: str
    cooking_experience: str
    health_issues: Optional[List[str]] = []
    eating_frequency: str  
    meal_count: Optional[int] = None 
    bmi: Optional[float]
    bmi_category: Optional[str]
    is_pro: bool = False
    regenerate_count: Optional[int] = 0

     
