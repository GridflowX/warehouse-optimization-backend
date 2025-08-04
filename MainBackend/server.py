from fastapi import FastAPI, HTTPException
from beckn_routes import router as beckn_router
from health_routes import router as health_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(beckn_router)
app.include_router(health_router)