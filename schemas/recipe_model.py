from pydantic import BaseModel
from typing import List, Optional

class RecipeRequest(BaseModel):
    ingredients: List[str]
    tags: List[str] = []
    lifestyle: Optional[str] = None
    is_pro: Optional[bool] = False
