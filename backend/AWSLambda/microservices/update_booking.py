# Get all bookings endpoint
# api/v1/bookings

# /api/v1/bookings POST

import boto3
import json

from backend.AWSLambda.database.BookingsTable import Booking

from backend.exceptions.bookings import *
from fastapi import status, HTTPException

from models.pydantic.booking import BookingUpdate, BookingCreate


# MM20250421: rely on API gateway for correct path and HTTP method
# MM20250421: think about authentication!
def handler(event, context):
    try:
    # from boto3 import client as boto3_client
    # lambda_client = boto3_client('lambda', region_name='eu-west-1')
    #     response = boto3_client.invoke(
    #         FunctionName='target-lambda-function-name',
    #         InvocationType='RequestResponse',  # or 'Event' for async invocation
    #         Payload=json.dumps(event)
    #     )

    if ('id' not in event['queryStringParameters']):
        raise HTTPException("Missing required parameter 'id'", status.HTTP_400_BAD_REQUEST)


    body = json.loads(event.get('body', '{}'))
    # old_booking = get_bookings(body.id)
    old_booking = Booking()
    update = BookingUpdate(**body)

    new_booking = Booking(
        id=old_booking.id,
        user_id=old_booking.user_id,
        car_id=old_booking.car_id,
        start_date=update.start_date,
        end_date=update.end_date,
        status=update.status,
        planned_pickup_time=old_booking.planned_pickup_time,
        pickup_date=update.planned_pickup_date,
        return_date=update.return_date,
        total_cost=old_booking.total_cost,
        currency_code=old_booking.currency_code,
        exchange_rate=old_booking.exchange_rate,
        status=old_booking.status

        user=old_booking.user,
        car=old_booking.car,
    )



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