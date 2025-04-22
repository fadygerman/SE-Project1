from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from currency_converter.client import get_currency_converter_client_instance
from exceptions.cars import CarNotFoundException
from exceptions.currencies import InvalidCurrencyException
from models.currencies import Currency
from models.db_models import Car as CarDB
from models.pydantic.car import Car


def get_all_cars(db: Session, currency_code: Optional[str] = Currency.USD.value) -> List[Car]:
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


def get_car_by_id(car_id: int, db: Session, currency_code: Optional[str] = Currency.USD.value) -> Car:
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
