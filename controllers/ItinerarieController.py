from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from services.genetic_algorithm.run import ag_service

itinerary_router = APIRouter()

class PlaceRequest(BaseModel):
    name: str
    lat: str
    lon: str
    time: str | None = None
    cost: str
    
class ItineraryRequest(BaseModel):
    hours: str
    quote: str
    places: List[PlaceRequest]

@itinerary_router.post("/create")
async def create_itinerarie(createItinerary: ItineraryRequest):
    try:
        places_dict = [place.dict() for place in createItinerary.places]
        best_route = ag_service(places_dict, createItinerary.hours, createItinerary.quote)
        return {"message": best_route}
    except Exception as e:
        return {"message": str(e)}

@itinerary_router.get("/{id}")
async def search_itinerarie(itinerarie_uuid):
    return {"item_id": itinerarie_uuid}

@itinerary_router.get("/history/{user_uuid}")
async def history(user_uuid ):
    return {"message": user_uuid}