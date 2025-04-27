import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.v1 import auth_routes, booking_routes, car_routes, user_routes

# Initialize FastAPI app
app = FastAPI(
    title="Car Rental API",
    description="Backend API for Car Rental Application",
    version="0.1.0"
)

# Get frontend URL from environment variable with a default fallback
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include versioned routers for API endpoints
app.include_router(car_routes.router, prefix="/api/v1")
app.include_router(user_routes.router, prefix="/api/v1")
app.include_router(booking_routes.router, prefix="/api/v1")
app.include_router(auth_routes.router, prefix="/api/v1")

# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)