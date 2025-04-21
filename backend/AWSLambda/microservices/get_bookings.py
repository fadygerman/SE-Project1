# Get all bookings endpoint
# api/v1/bookings

# /api/v1/bookings GET

import boto3
import json

from backend.AWSLambda.database.BookingsTable import BookingsTable

from backend.exceptions.bookings import *
from fastapi import status, HTTPException

# MM20250421: rely on API gateway for correct path
# MM20250421: think about authentication!
def handler(event, context):
    try:
        if ('id' in event['queryStringParameters']):
            return BookingsTable.get_bookings_by_id(event['queryStringParameters']['id'])
        else:
            return BookingsTable.get_bookings_by_id()


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

