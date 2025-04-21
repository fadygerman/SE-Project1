# /api/v1/bookings POST

import boto3
import json

from models.pydantic.booking import Booking, BookingCreate, BookingStatus
from backend.AWSLambda.database.BookingsTable import BookingsTable

from backend.exceptions.bookings import *
from fastapi import status, HTTPException

from services.booking_service import calculate_booking_duration


def handler(event, context):
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        request_booking = BookingCreate(**body)

        #MM20250421: ask car lambda for car details
        #             - car["price"]
        car_price = 1;
        total_cost = calculate_booking_duration(request_booking.start_date, request_booking.end_date) * car_price

        #MM20250421: ask currency lambda for exchangerate
        #             - response["exchange_rate"]
        exchange_rate = 1;

        complete_booking = Booking(
            user_id=request_booking.user_id,
            car_id=request_booking.car_id,
            start_date=request_booking.start_date,
            end_date=request_booking.end_date,
            planned_pickup_time=request_booking.planned_pickup_time,  # Store time in UTC (without timezone)
            total_cost=total_cost,
            currency_code=request_booking.currency_code,
            exchange_rate=exchange_rate,
            status=BookingStatus.PLANNED
        )

        return BookingsTable.add_booking(complete_booking)
    except NoCarFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except (
        CarNotAvailableException,
        BookingOverlapException,
        BookingStartDateException
    ) as e:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=e.message
    )
