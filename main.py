from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from routes.itab import router as itab_router
from routes.cascade import router as cascade_router
from routes.download import router as download_router
from routes.dossie_log import router as dossie_log_router
from routes.administration import router as admin_router
from routes.notification import router as ws_router
from routes.simdata import router as sim_router


app = FastAPI()

# CORS settings
origins = [
    "*",
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
app.include_router(admin_router)
app.include_router(ws_router)
app.include_router(sim_router)
