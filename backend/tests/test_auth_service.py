from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.services.auth_service import authenticate_user, create_user, get_user_by_email


def test_create_user_and_authenticate_roundtrip():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        user = create_user(db, email="u@example.com", password="pass123", full_name="User")
        assert user.id is not None
        assert user.email == "u@example.com"
        assert user.balance == 100

        fetched = get_user_by_email(db, "u@example.com")
        assert fetched is not None
        assert fetched.id == user.id

        assert authenticate_user(db, "u@example.com", "pass123").id == user.id
        assert authenticate_user(db, "u@example.com", "wrong") is False
        assert authenticate_user(db, "missing@example.com", "pass123") is False
    finally:
        db.close()

