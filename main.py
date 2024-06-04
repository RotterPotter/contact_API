import uvicorn 
import fastapi
import contacts.routes
import auth.routes
from auth.service import Service
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from slowapi import  _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from limiter_config import limiter


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    global limiter


    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded, _rate_limit_exceeded_handler
    )

    yield

app = fastapi.FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:4000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.routes.router, dependencies=[fastapi.Depends(Service.get_current_user)])
app.include_router(contacts.routes.router_debug, dependencies=[fastapi.Depends(Service.get_current_user)])

app.include_router(auth.routes.router)
app.include_router(auth.routes.router_debug)

if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8000, reload=True
    )