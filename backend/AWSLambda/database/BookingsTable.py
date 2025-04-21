import json

import botocore
import boto3
import logging

from boto3.dynamodb.conditions import Key, Attr

from models.pydantic.booking import Booking
from exceptions.bookings import BookingOverlapException, BookingNotFoundException

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
            dyn_resource = boto3.resource('dynamodb')
        table = self.dyn_resource.Table("bookings")
        table.delete()

    def create_table(self):
        """
        only need the separate index definitions by themselves
         - choose primary key for fast availability check when create_booking
         - choose secondary key 'get_booking_efficiently' for fast per booking retrieval when update_booking
        """
        try:
            self.table = self.dyn_resource.create_table(
                TableName="bookings",
                KeySchema=[
                    {"AttributeName": "car_id", "KeyType": "HASH"},  # sort the entries per car
                    {"AttributeName": "start_date", "KeyType": "RANGE"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'get_booking_efficiently',
                        'KeySchema': [
                            {
                                'AttributeName': 'id',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {     # according to https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_Projection.html
                            'ProjectionType': 'KEYS_ONLY'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 1,
                            'WriteCapacityUnits': 1
                        }
                    }
                ],
                AttributeDefinitions=[
                    {"AttributeName": "car_id", "AttributeType": "N"},
                    {"AttributeName": "start_date", "AttributeType": "S"},
                    {"AttributeName": "id", "AttributeType": "N"},
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

        overlapping_bookings = self.table.query(KeyConditionExpression=Key("car_id").eq(booking_json["car_id"]) & Key("start_date").lt(booking_json["end_date"]),
                                                FilterExpression=~(Attr("end_date").gt(booking_json["start_date"])))

        if len(overlapping_bookings["Items"]) > 0:
            raise BookingOverlapException(booking_json["car_id"])

        return self.table.put_item(Item=booking_json)

    def get_bookings_by_id(self, booking_index: int = None):
        if self.table is None:
            logger.error("Table {} not created",
                         "testTableName")
            raise Exception("Create table '{}' first".format("testTableName"))

        if (booking_index is None):
            return self.table.scan()
        else:
            return self.table.get_item(Key={"id": booking_index}, ConsistentRead=True)  # want to avoid failing checks

    def put_booking(self, booking: Booking):
        if self.table is None:
            logger.error("Table {} not created",
                         "testTableName")
            raise Exception("Create table '{}' first".format("testTableName"))

        booking_json = json.loads(booking.model_dump_json())

        value = self.table.get_item(Key={"id": booking_json["id"]}, ConsistentRead=True)

        if len(value["Item"]) > 0:
            return self.table.put_item(Item=booking_json)
        else:
            raise BookingNotFoundException(booking_json["id"])








