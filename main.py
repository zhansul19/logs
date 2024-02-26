from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from routes.itab import router as itab_router
from routes.cascade import router as cascade_router
from routes.download import router as download_router
from routes.dossie_log import router as dossie_log_router

app = FastAPI()

# CORS settings
origins = [
    "http://localhost:3000",
]
# Add CORS middleware to allow requests from specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Import and define route handlers
app.include_router(auth_router)
app.include_router(itab_router)
app.include_router(cascade_router)
app.include_router(download_router)
app.include_router(dossie_log_router)

