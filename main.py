import uvicorn 
import fastapi
import contacts.routes

app = fastapi.FastAPI()
app.include_router(contacts.routes.router)
app.include_router(contacts.routes.router_debug)
if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8000, reload=True
    )