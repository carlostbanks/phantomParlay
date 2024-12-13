from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import bets

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bets.router, prefix="/api/v1/bets", tags=["bets"])

@app.get("/")
async def read_root():
    return {"message": "Parlay Pulse API is running!"}