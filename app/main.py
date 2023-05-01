from fastapi import FastAPI, Depends, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from databases import Database

from app.routers import events, auth, users, reservations, menu_item
from app.settings import settings
from app.dependencies import create_admin


engine = create_engine(settings.DB_URI)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3000/",
    "http://localhost"
    "http://localhost/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(reservations.router)
app.include_router(menu_item.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

database = Database(settings.DB_URI)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/create-user')
async def create_user(admin = Depends(create_admin)):
    return Response(status_code=status.HTTP_201_CREATED)

