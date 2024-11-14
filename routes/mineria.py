from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict
from routes.database import get_db

router = APIRouter()

@router.get("/")
async def hello_world():
    return {"message": "¡Bienvenido a la API de FastAPI!"}

@router.get("/vistas", response_model=List[Dict[str, int]])
async def get_vistas_por_dia(db: AsyncSession = Depends(get_db)):
    query = """
    SELECT 
      COUNT(*) AS vistas, 
      DATE(created_at) AS fecha
    FROM views
    GROUP BY DATE(created_at)
    ORDER BY fecha;
    """
    # Ejecutar la consulta de forma asíncrona
    result = await db.execute(text(query))
    print(result)
    rows = result.fetchall()
    
    # Convertir el resultado a una lista de diccionarios
    return [{"vistas": row.vistas, "fecha": row.fecha} for row in rows]
