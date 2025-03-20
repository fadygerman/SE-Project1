import enum
from sqlalchemy import Boolean, Column, Date, Enum, Float, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import relationship
from database import Base

class BookingStatus(enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    CANCELED = "canceled"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(150), unique=True, index=True)
    phone_number = Column(String(20), unique=True)
    password_hash = Column(String(255))
    
    # Relationship to bookings
    bookings = relationship("Booking", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

class Car(Base):
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    model = Column(String(50))
    price_per_day = Column(Numeric(10, 2))
    is_available = Column(Boolean, default=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Relationship to bookings
    bookings = relationship("Booking", back_populates="car")
    
    def __repr__(self):
        return f"<Car(id={self.id}, name={self.name}, model={self.model})>"

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    car_id = Column(Integer, ForeignKey("cars.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    pickup_date = Column(Date, nullable=True)
    return_date = Column(Date, nullable=True)
    total_cost = Column(Numeric(10, 2))
    status = Column(Enum(BookingStatus))
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    car = relationship("Car", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, user_id={self.user_id}, car_id={self.car_id})>"