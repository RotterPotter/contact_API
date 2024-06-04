import uvicorn 
import fastapi
import contacts.routes
import auth.routes
from auth.service import Service
from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()

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