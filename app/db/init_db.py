from app.db.session import engine
from app.db.base import Base
from app.models.user import User 
from app.models.calculation import Calculation

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("DB initialized.")
