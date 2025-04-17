# Car Rental Backend API

## Overview
REST API backend for the Car Rental Web Application built using Python FastAPI. Provides authentication, car listing, booking management and payment processing functionality. Features comprehensive test coverage with pytest for reliability and maintainability.

## Features
- RESTful API endpoints for cars, users, and bookings with versioning support
- SQLite database with SQLAlchemy ORM
- Pydantic models with advanced validation and field documentation
- API versioning for backward compatibility
- Email validation and field validation rules
- Full OpenAPI/Swagger documentation
- Comprehensive test suite with pytest and class-based organization
- Mock-based testing for date-dependent operations
- Simple, lightweight implementation
- Ready for integration with Currency Converter Service and Google Maps

## Technology Stack
- **Language**: Python 3.9+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite (local development), PostgreSQL (in progress)
- **Documentation**: OpenAPI/Swagger (built into FastAPI)
- **Validation**: Pydantic with email-validator
- **Testing**: pytest, pytest-cov, unittest.mock
- **Test Client**: FastAPI TestClient

## Project Structure
```
backend/
├── models/
├── routes/
├── tests/
├── database.py
├── main.py
└── requirements.txt
```

## Access API documentation
   - http://127.0.0.1:8000/docs (Swagger UI)
   - http://127.0.0.1:8000/redoc (ReDoc)

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
4. Copy `.env.example` file in the root directory and set the values.
   - default values do not need to be changed for local development with PostgreSQL
5. Start the database using Docker Compose:
   ```
   docker compose up
   ```
   This will start a PostgreSQL database and automatically initialize it with sample data.

6. Start development server:
   ```
   uvicorn main:app --reload
   ```
   or
   ```
   python main.py
   ```


## Implemented Enhancements

- API versioning for backward compatibility
- Field validation rules with descriptive error messages
- Email address validation using email-validator
- Request/response model validation with Pydantic
- Absolute path configuration for database file location
- Field documentation for improved OpenAPI documentation

## Testing

### Requirements
- Docker must be installed on your system to run tests
  - as the tests use PostgreSQL containers via the `testcontainers` package.

### Running Tests
The project uses pytest for automated testing. To run the tests:

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_booking_routes.py
```
### Test Structure
Tests are organized using pytest class-based structure for better organization:

#### Booking Tests
- **TestBookingCreation**: Tests for creating bookings
- **TestBookingDateUpdates**: Tests for updating booking dates
- **TestBookingStatusTransitions**: Tests for status transitions
- **TestBookingErrorHandling**: Tests for API error handling
- **TestBookingRetrieval**: Tests for retrieving bookings 
- **TestBookingEdgeCases**: Tests for edge cases

#### Car Tests
- **TestCarRetrieval**: Tests for retrieving cars and filtering

#### User Tests
- **TestUserRetrieval**: Tests for user lookup and profile retrieval

### Testing Approach

#### Fixtures
Tests use fixtures defined in `conftest.py` including:
- Database fixture (`test_db`) - SQLite in-memory database
- Test data fixture (`test_data`) - sample users, cars and bookings
- API client fixture (`client`) - FastAPI test client

#### Mocking
Unit tests use the `unittest.mock` library to simulate:
- Current date (`patch('routes.v1.booking_routes.date')`)
- External dependencies

#### Parameterized Tests
Complex validation logic is tested with parameterized tests:
```python
@pytest.mark.parametrize("date_func,field,error_message", [
    (lambda b: b.start_date - timedelta(days=1), "pickup_date", "within the booking period"),
    (lambda b: b.end_date + timedelta(days=1), "pickup_date", "within the booking period"),
])
def test_date_validation_parametrized(client, test_data, date_func, field, error_message):
    # Test implementation
```

### Test Coverage
The test suite provides comprehensive coverage of:
- All REST API endpoints (GET, POST, PUT)
- Business logic validation rules
- Error handling scenarios
- Status transitions (PLANNED → ACTIVE → COMPLETED)
- Date and time validations
- Edge cases and validation errors

### Test Configuration
Custom pytest settings are in `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
```

## Planned Enhancements

### Authentication & Authorization
- User registration and login endpoints
- AWS AUTH0 integration for secure authentication
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
- Filtering options for car listings
- Pagination for list endpoints
- Booking creation, modification, and cancellation
- Payment processing functionality

### Testing & Documentation
- AWS configuration documentation
- Deployment instructions

## License
TBD