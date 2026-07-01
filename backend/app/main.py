from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import dashboard, enroll, risk, session, verify
from app.db.init_db import init_db

app = FastAPI(title="TrustPulse")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(enroll.router)
app.include_router(verify.router)
app.include_router(session.router)
app.include_router(risk.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "TrustPulse"}
