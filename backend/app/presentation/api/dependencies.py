from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.infrastructure.database.session import get_session
async def session_dep(session: AsyncSession=Depends(get_session)): return session
async def internal_auth(x_internal_api_key: str=Header(default="")):
    if not secrets_compare(x_internal_api_key, get_settings().internal_api_key): raise HTTPException(401, "Invalid internal API key")
def secrets_compare(a,b):
    import hmac
    return hmac.compare_digest(a,b)

