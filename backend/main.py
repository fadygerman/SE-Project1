from fastapi import FastAPI
from routes.v1 import car_routes, user_routes, booking_routes, auth_routes
from utils.auth import configure_auth

# Initialize FastAPI app
app = FastAPI(
    title="Car Rental API",
    description="Backend API for Car Rental Application",
    version="0.1.0"
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Car Rental API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Configure auth and session
configure_auth(app)

# Include routers
app.include_router(auth_routes.router, prefix="/api/v1")
app.include_router(car_routes.router, prefix="/api/v1")
app.include_router(user_routes.router, prefix="/api/v1")
app.include_router(booking_routes.router, prefix="/api/v1")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)