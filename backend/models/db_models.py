import enum
from sqlalchemy import Boolean, Column, Date, Enum, Float, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import relationship
from database import Base

class BookingStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELED = "canceled"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True)
    password_hash = Column(String)
    
    # Relationship to bookings
    bookings = relationship("Booking", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

class Car(Base):
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    model = Column(String)
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
    total_cost = Column(Numeric(10, 2))
    status = Column(Enum(BookingStatus))
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    car = relationship("Car", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, user_id={self.user_id}, car_id={self.car_id})>"