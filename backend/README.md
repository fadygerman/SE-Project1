# Car Rental Backend API

## Overview
REST API backend for the Car Rental Web Application built using Python FastAPI. Provides authentication, car listing, booking management and payment processing functionality.

## Features
- AWS Cognito integration for user authentication
- RESTful API endpoints for cars, users, and bookings
- PostgreSQL database with SQLAlchemy ORM
- Deployment on AWS (Lambda or EC2)
- Integration with Currency Converter Service
- Integration with Google Maps

## Technology Stack
- **Language**: Python 3.9+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Authentication**: AWS Cognito
- **Deployment**: AWS (Lambda/EC2)
- **Documentation**: OpenAPI/Swagger

## Project Structure
```
backend/
├── app/
│   ├── models/         # SQLAlchemy data models
│   ├── routes/         # API endpoint routes
│   ├── services/       # Business logic services
│   ├── schemas/        # Pydantic schemas/validators
│   ├── utils/          # Helper utilities
│   └── config.py       # Configuration
├── migrations/         # Alembic database migrations
├── tests/              # Test suite
├── requirements.txt    # Dependencies
├── Dockerfile          # Container definition
├── main.py             # Application entrypoint
└── README.md
```

## API Endpoints

### User Endpoints
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /users` - List all users (admin)
- `GET /users/{id}` - Get user details

### Car Endpoints
- `GET /cars` - List all cars with filtering
- `GET /cars/{id}` - Get specific car details

### Booking Endpoints
- `GET /bookings` - List user's bookings
- `POST /bookings` - Create new booking
- `GET /bookings/{id}` - Get booking details
- `PUT /bookings/{id}` - Update booking
- `DELETE /bookings/{id}` - Cancel booking

## Setup Instructions
1. Clone the repository
2. Create and activate virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```
   cp .env.example .env
   # Edit .env with your database and AWS credentials
   ```
5. Run database migrations:
   ```
   alembic upgrade head
   ```
6. Start development server:
   ```
   uvicorn app.main:app --reload
   ```

## AWS Configuration
1. Create Cognito User Pool
2. Set up IAM roles for API access
3. Configure environment variables with AWS credentials

## Testing
Run tests with pytest:
```
pytest
```

## Deployment
Instructions for AWS deployment will be provided in separate documentation.

## License
TBD