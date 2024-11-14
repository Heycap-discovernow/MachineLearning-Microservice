from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Actualiza la URL para usar asyncpg
DATABASE_URL = "postgresql+asyncpg://admin:adminadmin@localhost/heycap"

# Crear un motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear una sesión asíncrona
async_session = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependencia para obtener la sesión de la base de datos
async def get_db():
    async with async_session() as session:
        yield session
