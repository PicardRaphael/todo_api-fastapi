from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import asyncio


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout=10):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout)
        except asyncio.TimeoutError:
            return JSONResponse(
                {"detail": "Request timeout. Please try again."},
                status_code=504,
            )
