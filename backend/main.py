import dotenv
import os
from pathlib import Path

dotenv.load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.v1 import car_routes, user_routes, booking_routes, auth_routes

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

# Define the path to your React build output
dist_path = Path("./dist").resolve()

# Verify that the dist directory exists
if not dist_path.exists() or not dist_path.is_dir():
    raise RuntimeError(f"React build directory not found at {dist_path}. Please build the React app first.")

# Mount the static files from the React build
app.mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="assets")

# Serve index.html for the root path
@app.get("/")
async def serve_index():
    index_path = dist_path / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found in build directory")
    return FileResponse(str(index_path))

# Catch-all route to support client-side routing
@app.get("/{path:path}")
async def serve_spa(path: str):
    # First check if the requested file exists in the dist folder
    requested_path = dist_path / path
    
    if requested_path.exists() and requested_path.is_file():
        # If the file exists, serve it directly
        return FileResponse(str(requested_path))
    else:
        # Otherwise, serve the index.html to support client-side routing
        index_path = dist_path / "index.html"
        return FileResponse(str(index_path))

# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)