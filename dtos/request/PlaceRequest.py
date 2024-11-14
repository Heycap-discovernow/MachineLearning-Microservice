from pydantic import BaseModel

class PlacesArray(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None