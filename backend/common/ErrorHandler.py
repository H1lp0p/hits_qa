from fastapi import Request

from .exceptions import CustomException

async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as ex:
        if isinstance(ex, CustomException):
            return ex.response()
    
        raise ex