import json

import botocore
import boto3
import logging

from boto3.dynamodb.conditions import Key, Attr

from backend.models.pydantic.booking import Booking, BookingCreate
from exceptions.bookings import BookingOverlapException

# Set up our logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class BookingsTable:
    def __init__(self, dyn_resource):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        # The table variable is set during the scenario in the call to
        # 'exists' if the table exists. Otherwise, it is set by 'create_table'.
        self.table = None

    def delete_table(self, dyn_resource = None):
        if self.dyn_resource is None:
            dyn_resource = boto3.resource("dynamodb")
        table = self.dyn_resource.Table("testTableName")
        table.delete()

    def create_table(self, table_name):
        """
        MM20250420: research for better table configuration, in particular, KeySchema!
        """
        try:
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "car_id", "KeyType": "HASH"},  # sort the entries per car
                    # {"AttributeName": "start_date", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "car_id", "AttributeType": "N"},
                    # {"AttributeName": "start_date", "AttributeType": "S"},
                ],
                BillingMode='PAY_PER_REQUEST',
            )
        except botocore.exceptions.ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return self.table

    def get_table(self):
        if not self.table is None:
            return self.table
        else:
            return self.table.create_table("testTableName")

    def add_booking(self, booking: Booking):
        if self.table is None:
            logger.error("Table {} not created",
                         "testTableName")
            raise Exception("Create table '{}' first".format("testTableName"))

        booking_json = json.loads(booking.model_dump_json())

        overlapping_bookings = self.table.query(KeyConditionExpression=Key("car_id").eq(booking_json["car_id"]),
                                                FilterExpression=~(Attr("start_date").gt(booking_json["end_date"]) | Attr("end_date").lt(booking_json["start_date"])))

        if len(overlapping_bookings["Items"]) > 0:
            raise BookingOverlapException(booking_json["car_id"])

        return self.table.put_item(Item=booking_json)

    def get_bookings(self):
        if self.table is None:
            logger.error("Table {} not created",
                         "testTableName")
            raise Exception("Create table '{}' first".format("testTableName"))

        return self.table.scan()







