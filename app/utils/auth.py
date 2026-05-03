from fastapi import Request, HTTPException
import jwt

SECRET_KEY = "this_is_my_super_secure_secret_key_12345"
ALGORITHM = "HS256"


def get_current_user(request: Request):
    token = request.headers.get("Authorization")

    # 🔥 fallback for download links
    if not token:
        token = request.query_params.get("token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")

    except:
        raise HTTPException(status_code=401, detail="Invalid token")