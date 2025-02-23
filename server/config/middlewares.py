from fastapi import Request, HTTPException

from server.config.db import SessionLocal


def authenticate_user(request: Request):
    key = request.headers.get("X-Authorization")
    lang = request.headers.get("Accept-Language")
    # TODO: check lang if it is in [uz ru en]
    if not key:
        raise HTTPException(status_code=401, detail="Authentication required")

    db = SessionLocal()
    try:
        my_auth_key = db.query(Token).filter(Token.key == key).first()

        if not my_auth_key:
            raise HTTPException(status_code=401, detail="Invalid key")

        # decoded_auth_key = decode_jwt(my_auth_key.key)
        # if not decoded_auth_key:
        #     raise HTTPException(status_code=401, detail="Invalid key")

        return {"token": my_auth_key.key, "lang": lang, "user": my_auth_key.owner}
    finally:
        db.close()

