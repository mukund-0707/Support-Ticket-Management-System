from fastapi import Request
import time
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from app.database import SessionLocal
from models.users import User
from starlette.middleware.base import BaseHTTPMiddleware


class ActiveUserMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        if request.url.path in ["/login", "/register"]:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            db = None

            try:
                payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
                email = payload.get("sub")

                db = SessionLocal()
                user = db.query(User).filter(User.email == email).first()

                if user and not user.is_active:
                    return JSONResponse(
                        status_code=403, content={"detail": "Your account is inactive"}
                    )

            except JWTError:
                pass
            finally:
                if db:
                    db.close()

        return await call_next(request)


async def common_middleware(request: Request, call_next):

    if request.url.path in ["/login", "/register"]:
        return await call_next(request)
    print(request)
    start = time.time()

    print(f"Request: {request.method} {request.url}")

    try:
        response = await call_next(request)
    except Exception as e:
        print("Error:", e)
        raise

    process_time = time.time() - start
    print(f"Time: {process_time}")

    return response
