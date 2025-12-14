from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import models, database
import schemas, crud
from config import ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_SECRET

models.Base.metadata.create_all(bind=database.engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    db = database.SessionLocal()
    admin_user = crud.get_user_by_username(db, username=ADMIN_USERNAME)
    if not admin_user:
        user_in = schemas.UserCreate(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        crud.create_user(db, user_in)
    db.close()
    yield
    # on shutdown

app = FastAPI(lifespan=lifespan)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to BettyIA"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/admin/")
def read_admin_secret(admin_secret: str = Header(None)):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"message": "Welcome, admin!"}
