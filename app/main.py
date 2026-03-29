from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from fastapi.responses import JSONResponse
import time

from app.api import leads, seeds, proxies, stats, jobs, n8n

app = FastAPI(title="Leadgen API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "msg": str(e)}
        )

app.include_router(leads.router, prefix="/leads", tags=["Leads"])
app.include_router(seeds.router, prefix="/seeds", tags=["Seeds"])
app.include_router(proxies.router, prefix="/proxies", tags=["Proxies"])
app.include_router(stats.router, prefix="/stats", tags=["Stats"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(n8n.router, prefix="/n8n", tags=["N8N Integration"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
