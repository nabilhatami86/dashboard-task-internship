from pydantic import BaseModel

class CategoryCreateSchema(BaseModel):
    name: str
    description: str | None = None

class CategoryUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None

class CategoryResponseSchema(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        from_attributes = True 
