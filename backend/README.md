# Car Rental Backend API

## Overview
REST API backend for the Car Rental Web Application built using Python FastAPI. Provides authentication, car listing, booking management and payment processing functionality.

## Features
- RESTful API endpoints for cars, users, and bookings with versioning support
- SQLite database with SQLAlchemy ORM
- Pydantic models with advanced validation and field documentation
- API versioning for backward compatibility
- Email validation and field validation rules
- Full OpenAPI/Swagger documentation
- Simple, lightweight implementation 
- Ready for integration with Currency Converter Service and Google Maps

## Technology Stack
- **Language**: Python 3.9+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite (local development), PostgreSQL (in progress)
- **Documentation**: OpenAPI/Swagger (built into FastAPI)
- **Validation**: Pydantic with email-validator

## Project Structure
```
backend/
├── models/            # Data models
│   ├── db_models.py   # SQLAlchemy database models
│   └── models.py      # Pydantic models/schemas
├── routes/            # API endpoint routes
│   └── v1/            # Version 1 API endpoints
│        ├── car_routes.py
│        ├── booking_routes.py
│        └── user_routes.py
├── database.py        # Database connection configuration
├── main.py            # Application entrypoint
├── db_seed.py         # Database seeding script
├── requirements.txt   # Dependencies
└── README.md
```

## API Endpoints

### Root Endpoints
- `GET /` - Welcome message
- `GET /health` - Health check

### User Endpoints
<!-- - `POST /api/v1/register` - Register new user
- `POST /api/v1/login` - User login -->
- `GET /api/v1/users` - List all users 
- `GET /api/v1/users/{id}` - Get user details

### Car Endpoints
- `GET /api/v1/cars` - List all cars with filtering
- `GET /api/v1/cars/{id}` - Get specific car details

### Booking Endpoints
- `GET /api/v1/bookings` - List user's bookings
- `GET /api/v1/bookings/{id}` - Get booking details
- `POST /api/v1/bookings` - Create new booking
<!-- - `PUT /api/v1/bookings/{id}` - Update booking
- `DELETE /api/v1/bookings/{id}` - Cancel booking -->

## Setup Instructions
1. Clone the repository
2. Create and activate virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Initialize and seed the database:
   ```
   python db_seed.py
   ```
5. Start development server:
   ```
   uvicorn main:app --reload
   ```
   or
   ```
   python main.py
   ```
6. Access API documentation:
   - http://127.0.0.1:8000/docs (Swagger UI)
   - http://127.0.0.1:8000/redoc (ReDoc)

## Data Models

### User
- `id`: Integer (Primary Key)
- `first_name`: String
- `last_name`: String
- `email`: EmailStr (Unique, validated)
- `phone_number`: String (Unique, validated)
- `password_hash`: String (excluded from responses)

### Car
- `id`: Integer (Primary Key)
- `name`: String
- `model`: String
- `price_per_day`: Decimal (validated > 0)
- `is_available`: Boolean
- `latitude`: Float (for map integration)
- `longitude`: Float (for map integration)

### Booking
- `id`: Integer (Primary Key)
- `user_id`: Foreign Key (User)
- `car_id`: Foreign Key (Car)
- `start_date`: Date (validated)
- `end_date`: Date (validated to be after start_date)
- `pickup_date`: Date (Optional)
- `return_date`: Date (Optional, validated against pickup_date)
- `total_cost`: Decimal (validated > 0)
- `status`: Enum (PLANNED, ACTIVE, COMPLETED, CANCELED, OVERDUE)

## Implemented Enhancements

- API versioning for backward compatibility
- Field validation rules with descriptive error messages
- Email address validation using email-validator
- Request/response model validation with Pydantic
- Absolute path configuration for database file location
- Field documentation for improved OpenAPI documentation

## Planned Enhancements

### Authentication & Authorization
- User registration and login endpoints
- AWS Cognito integration for secure authentication
- Role-based access control

### Database & Infrastructure
- Migration to PostgreSQL database
- Deployment on AWS (Lambda/EC2)
- CI/CD pipeline setup
- Implement soft deletion (is_active flag)
- Add timestamps (created_at, updated_at)

### Additional Features
- Complete CRUD operations for all entities
- Integration with Currency Converter Service
- Integration with Google Maps API
- Filtering options for car listings
- Pagination for list endpoints
- Booking creation, modification, and cancellation
- Payment processing functionality

### Testing & Documentation
- Comprehensive unit and integration tests
- AWS configuration documentation
- Deployment instructions

## License
TBD