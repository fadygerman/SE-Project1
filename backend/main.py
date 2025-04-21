import dotenv

dotenv.load_dotenv()

from fastapi import FastAPI
from routes.v1 import car_routes, user_routes, booking_routes, auth_routes
from routes.v1 import car_routes, user_routes, booking_routes
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI app
app = FastAPI(
    title="Car Rental API",
    description="Backend API for Car Rental Application",
    version="0.1.0"
)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],              # or restrict to ["GET", "POST", ...]
    allow_headers=["*"],              # or restrict to specific headers
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Car Rental API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include versioned routers
app.include_router(car_routes.router, prefix="/api/v1")
app.include_router(user_routes.router, prefix="/api/v1")
app.include_router(booking_routes.router, prefix="/api/v1")
app.include_router(auth_routes.router, prefix="/api/v1")

# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)