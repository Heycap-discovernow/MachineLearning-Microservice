from fastapi import APIRouter, Depends
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

@router.get("/vistas", response_model=List[VistaResponse])
async def get_vistas_por_dia(db: AsyncSession = Depends(get_db)):
    query = """
    SELECT 
      COUNT(*) AS vistas, 
      DATE(created_at) AS fecha
    FROM views
    WHERE place_id = 199
    GROUP BY DATE(created_at)
    ORDER BY fecha;
    """
    result = await db.execute(text(query))
    rows = result.fetchall()
    
    return [{"vistas": row.vistas, "fecha": row.fecha} for row in rows]
