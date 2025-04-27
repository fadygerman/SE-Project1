import logging

from sqlalchemy import desc
from sqlalchemy.orm import Session

from currency_converter.client import get_currency_converter_client_instance
from exceptions.cars import CarNotFoundException
from exceptions.currencies import InvalidCurrencyException, CurrencyServiceUnavailableException
from models.currencies import Currency
from models.db_models import Car as CarDB
from models.pydantic.car import Car
from models.pydantic.pagination import PaginationParams, SortParams, PaginatedResponse


def get_all_cars(db: Session, currency_code: str | None = Currency.USD.value) -> list[Car]:
    cars_db = db.query(CarDB).all()
    cars = [Car.model_validate(car) for car in cars_db]
    
    if not currency_code or currency_code == Currency.USD:
        return cars
    
    try:
        currency = Currency(currency_code)
    except ValueError:
        raise InvalidCurrencyException(currency_code)
    
    currency_converter = get_currency_converter_client_instance()
    
    for car in cars:
        converted_price = currency_converter.convert("USD", currency.value, car.price_per_day)
        car.price_per_day = converted_price
    
    return cars


def get_car_by_id(car_id: int, db: Session, currency_code: str | None = Currency.USD.value) -> Car:
    car_db = db.query(CarDB).filter(CarDB.id == car_id).first()
    
    if car_db is None:
        raise CarNotFoundException(car_id)
    
    car = Car.model_validate(car_db)
    
    if not currency_code or currency_code == Currency.USD:
        return car
    
    try:
        currency = Currency(currency_code)
    except ValueError:
        raise InvalidCurrencyException(currency_code)
    
    currency_converter = get_currency_converter_client_instance()
    converted_price = currency_converter.convert("USD", currency.value, car.price_per_day)
    car.price_per_day = converted_price
    
    return car


def get_filtered_cars(
    db: Session,
    pagination: PaginationParams,
    name_filter: str | None = None,
    available_only: bool = False,
    currency_code: str = Currency.USD.value,
    sort_params: SortParams | None = None
) -> PaginatedResponse[Car]:
    """
    Get cars with filtering, sorting, and pagination.
    
    Args:
        db: Database session
        pagination: Pagination parameters
        name_filter: Optional filter for car name or model
        available_only: If True, return only available cars
        currency_code: Currency code for pricing
        sort_params: Optional sorting parameters
        
    Returns:
        PaginatedResponse containing cars and pagination metadata
    """
    # Start with base query
    query = db.query(CarDB)
    
    # Apply filters
    if name_filter:
        # Search both name and model fields
        query = query.filter(
            (CarDB.name.ilike(f'%{name_filter}%')) | (CarDB.model.ilike(f'%{name_filter}%'))
        )
    
    if available_only:
        query = query.filter(CarDB.is_available == True)
    
    # Apply sorting
    if sort_params:
        if hasattr(CarDB, sort_params.sort_by):
            sort_column = getattr(CarDB, sort_params.sort_by)
            
            if sort_params.sort_order == "desc":
                sort_column = desc(sort_column)
                
            query = query.order_by(sort_column)
        else:
            # Default to sorting by ID if column doesn't exist
            query = query.order_by(CarDB.id)
    else:
        # Default sort by ID
        query = query.order_by(CarDB.id)
    
    # Count total items for pagination metadata
    total_items = query.count()
    
    # Calculate total pages
    total_pages = (total_items + pagination.page_size - 1) // pagination.page_size if total_items > 0 else 0
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.page_size
    query = query.offset(offset).limit(pagination.page_size)
    
    # Execute query
    cars_db = query.all()
    
    # Check currency code first before processing cars
    if currency_code != Currency.USD.value:
        try:
            Currency(currency_code)
        except ValueError as ve:
            # Raise InvalidCurrencyException instead of just logging
            logging.warning(f"Invalid currency code '{currency_code}': {ve}")
            raise InvalidCurrencyException(currency_code)
    
    # Convert to Pydantic models with currency conversion if needed
    cars = []
    converter = None
    if currency_code != Currency.USD.value:
        try:
            currency = Currency(currency_code)  # This is already checked above, but kept for clarity
            converter = get_currency_converter_client_instance()
        except Exception as e:
            logging.error(f"Failed to initialize currency converter for '{currency_code}': {e}")
            raise CurrencyServiceUnavailableException(str(e))

    # Now use the converter in the loop
    for car_db in cars_db:
        car = Car.model_validate(car_db)
        
        # Convert pricing if needed
        if converter:
            try:
                car.price_per_day = converter.convert('USD', currency.value, car.price_per_day)
            except Exception as e:
                logging.error(f"Currency conversion failed for '{currency_code}': {e}")
                raise CurrencyServiceUnavailableException(str(e))
                
        cars.append(car)
    
    # Return paginated response
    return PaginatedResponse[Car](
        items=cars,
        total=total_items,
        page=pagination.page,
        page_size=pagination.page_size,
        pages=total_pages
    )
