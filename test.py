# main.py
from fastapi import FastAPI
from routes.mineria import router as mineria_router

app = FastAPI()

# Incluye los routers
app.include_router(mineria_router, prefix="/ml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# USA LA CARPETA REPOSITORIES PARA LA BASE DE DATOS ESTO PARA QUE ME FACILITES LA MIGRACION DE TUS RUTAS A EVENTOS DE MS Y NO PERDAMOS TANTO TIEMPO
# ANTES DEBES COMENTAR LO DE MAIN PARA PODER ENCENDER ESTA API QUE TRABAJA CON HTTP Y NO CON NATS