
import boto3
import logging

from backend.AWSLambda.database.BookingsTable import Booking, BookingsTable
from backend.models.pydantic.booking import BookingStatus

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

logger = logging.getLogger()

BookingService = BookingsTable(ddb)
print(BookingService)
testTable = BookingService.create_table("testTableName")
print(testTable)

booking1 = Booking(id=0,
status=BookingStatus.PLANNED,
user_id=1,
car_id=999,
start_date="2025-06-01",
end_date="2025-06-05",
planned_pickup_time="09:30:00",
currency_code="USD",
exchange_rate=1,
total_cost=1)

# new booking fails due to overlapping dates
booking2 = Booking(id=1,
status=BookingStatus.PLANNED,
user_id=2,
car_id=999,
start_date="2025-06-02",
end_date="2025-06-06",
planned_pickup_time="09:30:00",
currency_code="USD",
exchange_rate=1,
total_cost=1)

# new booking succeeds due to distinct dates
booking3 = Booking(id=2,
status=BookingStatus.PLANNED,
user_id=3,
car_id=999,
start_date="2025-06-07",
end_date="2025-06-08",
planned_pickup_time="09:30:00",
currency_code="USD",
exchange_rate=1,
total_cost=1)

#new booking succeeds due to distinct car_id
booking4 = Booking(id=3,
status=BookingStatus.PLANNED,
user_id=4,
car_id=1,
start_date="2025-06-01",
end_date="2025-06-05",
planned_pickup_time="09:30:00",
currency_code="USD",
exchange_rate=1,
total_cost=1)

try:
    print(BookingService.add_booking(booking1))
except Exception as err:
    logger.error(err)

try:
    print(BookingService.add_booking(booking2))
except Exception as err:
    logger.error(err)

try:
    print(BookingService.add_booking(booking3))
except Exception as err:
    logger.error(err)

try:
    print(BookingService.add_booking(booking4))
except Exception as err:
    logger.error(err)

print("all bookings:")
print(BookingService.get_bookings())

BookingService.delete_table(ddb)
'''
table = testTable.create_table("testTableName")
print(table)
testTable.delete_table()

testTable.delete_table(ddb)

BookingsTable = Bookings(dynamodb)

table = BookingsTable.create_table(table_name='testBookingsTable')

table.put_item(
    Item={
        'pk': 'id#1',
        'sk': 'cart#123',
        'name': 'SomeName',
        'inventory': 500,
        # ... more attributes ...
    }
)


'''
