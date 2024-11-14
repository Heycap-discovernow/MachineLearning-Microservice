from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Union
from routes.database import get_db
from datetime import date
from pydantic import BaseModel

router = APIRouter()

@router.get("/")
async def hello_world():
    return {"message": "¡Bienvenido a la API de FastAPI!"}

class VistaResponse(BaseModel):
    vistas: int
    fecha: date

@router.get("/vistas/{place_id}", response_model=List[VistaResponse])
async def get_vistas_por_dia(place_id: str, db: AsyncSession = Depends(get_db)):
  
  query = """
    SELECT place_id 
    FROM places 
    WHERE google_id = :google_id;
    """
  result = await db.execute(text(query), {"google_id": place_id})
  place = result.fetchone()
  
  if not place:
    raise HTTPException(status_code=404, detail="Error: place not found")
    
  query = """
  SELECT 
    COUNT(*) AS vistas, 
    DATE(created_at) AS fecha
  FROM views
  WHERE place_id = :place_id
  GROUP BY DATE(created_at)
  ORDER BY fecha;
  """
  result = await db.execute(text(query), {"place_id": place.place_id})
  rows = result.fetchall()
  
  return [{"vistas": row.vistas, "fecha": row.fecha} for row in rows]
