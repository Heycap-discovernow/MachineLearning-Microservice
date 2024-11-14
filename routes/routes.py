from fastapi import APIRouter
import dtos.request.PlaceRequest as placeRequest
from services.genetic_algorithm.run import ag

# AQUI SE TRABAJARA LO DEL AG

router = APIRouter()

@router.post("/create")
async def create_itinerarie():
    return {"message": "¡Bienvenido a la API de FastAPI!"}

@router.get("/{id}")
async def search_itinerarie(itinerarie_uuid):
    return {"item_id": itinerarie_uuid}

@router.get("/history/{user_uuid}")
async def history(user_uuid ):
    return {"message": user_uuid}