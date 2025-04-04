from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite database URL - this will create the database file in the current directory
DATABASE_URL = "sqlite:///./car_rental.db"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()