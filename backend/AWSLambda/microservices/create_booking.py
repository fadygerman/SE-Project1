# /api/v1/bookings POST

import boto3
import json

from models.pydantic.booking import BookingCreate
from backend.AWSLambda.database.BookingsTable import BookingsTable

from backend.exceptions.bookings import *
from fastapi import status, HTTPException

def handler(event, context):
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))

        booking = BookingCreate(**body)

        # ask get_car(id) lambda for availability

        return BookingsTable.add_booking(booking)
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
