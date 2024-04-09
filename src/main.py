import fastapi
import uvicorn

from src.routes.contacts import routes
from src.routes.users import routes as users_routes

app = fastapi.FastAPI()

app.include_router(routes.router)
app.include_router(users_routes.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
