from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.infrastructure.database.session import SessionFactory
from app.presentation.api.routes import internal, public, reviews
configure_logging(); settings=get_settings()
app=FastAPI(title="India Establishment Enforcement Map",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origin_list,allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["Content-Type","X-Internal-API-Key"])
app.include_router(public.router,prefix="/api/v1"); app.include_router(reviews.router,prefix="/api/v1"); app.include_router(internal.router,prefix="/api/v1")
@app.exception_handler(AppError)
async def app_error(_:Request,exc:AppError): return JSONResponse(status_code=exc.status_code,content={"error":{"code":exc.code,"message":exc.message}})
@app.get("/health")
async def health(): return {"status":"ok"}
@app.get("/ready")
async def ready():
    try:
        async with SessionFactory() as s: await s.execute(text("SELECT 1"))
        return {"status":"ready","database":"ok"}
    except Exception: return JSONResponse(status_code=503,content={"status":"not_ready","database":"unavailable"})

