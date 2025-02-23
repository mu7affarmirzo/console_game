import logging
from functools import wraps
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Callable, Any
from starlette.requests import Request

logger = logging.getLogger(__name__)


def handle_exceptions(func: Callable) -> Callable:
    """
    Decorator to handle exceptions in API routes with detailed error reporting.

    Args:
        func: The function to decorate

    Returns:
        Callable: Wrapped function with exception handling
    """

    @wraps(func)  # Preserves the metadata of the original function
    async def wrapper(*args, **kwargs) -> JSONResponse:
        # Try to extract request from args/kwargs for context
        request = next(
            (arg for arg in args if isinstance(arg, Request)), None
        ) or kwargs.get('request')

        try:
            return await func(*args, **kwargs)

        except HTTPException as http_exc:
            logger.warning(f"HTTP Exception: {http_exc.detail}")
            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "error": {
                        "message": str(http_exc.detail),
                        "code": http_exc.status_code
                    }
                }
            )

        except ValueError as ve:
            logger.warning(f"Validation Error: {str(ve)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "message": str(ve),
                        "code": 400
                    }
                }
            )

        except Exception as e:
            error_msg = f"Unexpected error in {func.__name__}: {str(e)}"
            logger.error(error_msg, exc_info=True)  # Log full stack trace
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": "Internal Server Error",
                        "code": 500,
                        "details": str(e) if request and request.app.debug else None
                    }
                }
            )

    return wrapper

