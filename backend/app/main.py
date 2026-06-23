from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.v1.router import api_router
from app.db.prisma import db
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    max_retries = 5
    for i in range(max_retries):
        try:
            await db.connect()
            logger.info("Successfully connected to Prisma.")
            break
        except Exception as e:
            logger.warning(f"Failed to connect to Prisma (attempt {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                await asyncio.sleep(2)
            else:
                logger.error("Could not connect to database after max retries. Server will start but DB queries may fail.")
    yield
    logger.info("Shutting down FastAPI - Disconnecting from Prisma...")
    await db.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Backend API is running."}
