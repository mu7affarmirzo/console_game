from fastapi.responses import JSONResponse

from server.db.models.all import Account
from server.utils.exception_handlers import handle_exceptions


@handle_exceptions
async def get_account_info(db, current_user: Account) -> JSONResponse:
    items = current_user.items
    creds = current_user.credits

    return JSONResponse(
        content={
            "items": items,
            "credits": creds,
        },
        status_code=200
    )

