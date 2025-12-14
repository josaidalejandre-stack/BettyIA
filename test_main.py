import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
from database import database, models
from database.database import Base
from config import ADMIN_USERNAME, ADMIN_SECRET

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    database.SessionLocal = TestingSessionLocal

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to BettyIA"}

def test_admin_user_created(client):
    db = TestingSessionLocal()
    admin_user = db.query(models.User).filter(models.User.username == ADMIN_USERNAME).first()
    db.close()
    assert admin_user is not None

def test_admin_endpoint_protected(client):
    response = client.get("/admin/")
    assert response.status_code == 403

    response = client.get("/admin/", headers={"admin-secret": "wrong_secret"})
    assert response.status_code == 403

    response = client.get("/admin/", headers={"admin-secret": ADMIN_SECRET})
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome, admin!"}
