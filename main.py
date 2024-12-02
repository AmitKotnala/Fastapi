from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.routers import auth
from app.routers import file_operations

app = FastAPI(
    title="Secure File Sharing System",
    description="A secure file sharing platform with role-based access control",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth.router)
app.include_router(file_operations.router)

@app.get("/")
def root():
    """
    Root endpoint for health check
    
    Returns:
        dict: Health check response
    """
    return {"message": "Secure File Sharing System is running"}

if __name__ == "__main__":
     uvicorn.run('main:app', host="0.0.0.0", port=8002,reload=True)